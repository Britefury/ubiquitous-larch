##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import threading
import sys

from collections import deque

import json

from copy import copy

from britefury.incremental.incremental_function_monitor import IncrementalFunctionMonitor

from britefury.dynamicsegments.segment import DynamicSegment, SegmentRef
from britefury.dynamicsegments import messages, dependencies
from britefury.dynamicsegments import global_dependencies
from britefury.inspector import present_exception


_page_content = u"""
<!doctype html>
<html>
	<head>
		<title>{title}</title>
		<link rel="stylesheet" type="text/css" href="/static/jquery/css/ui-lightness/jquery-ui-1.10.2.custom.min.css"/>
		<link rel="stylesheet" type="text/css" href="/static/larch.css"/>

		<script type="text/javascript" src="/static/jquery/js/jquery-1.9.1.js"></script>
		<script type="text/javascript" src="/static/jquery/js/jquery-ui-1.10.2.custom.min.js"></script>
		<script type="text/javascript" src="/static/noty/jquery.noty.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/bottom.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/bottomLeft.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/bottomCenter.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/bottomRight.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/center.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/centerLeft.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/centerRight.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/inline.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/top.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/topLeft.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/topCenter.js"></script>
		<script type="text/javascript" src="/static/noty/layouts/topRight.js"></script>
		<script type="text/javascript" src="/static/noty/themes/default.js"></script>
		<script type="text/javascript" src="/static/json2.js"></script>
		<script type="text/javascript" src="/static/larch.js"></script>
		<script type="text/javascript">
			<!--
			larch.__session_id="{session_id}";
			// -->
		</script>

		<!--scripts and css introduced by dependencies-->
		{dependency_tags}

		<!--initialisers; expressions that must be executed to initialise elements or the document-->
		<script type="text/javascript">
			<!--
			$(document).ready(function(){{larch.__onDocumentReady({initialisers});}});
			{init_script}
			// -->
		</script>
	</head>

	<body>
	<div class="__larch_page_header">
		Press ESC for command bar.
	</div>

	<img src="/static/1px_transparent.png">

	<div class="__larch_page_content">
		{content}
	</div>

	<!-- refresh on back button, adapted from http://www.webdeveloper.com/forum/showthread.php?137518-How-to-refresh-page-after-clicking-quot-Back-quot-button -->
	<input type="hidden" id="__larch_refreshed" value="0">
	<script type="text/javascript">
		onload = function(){{
			var refresh_elem =document.getElementById("__larch_refreshed");
			if(refresh_elem.value=="0") {{
				refresh_elem.value="1";
			}}
			else {{
				refresh_elem.value="0";
				location.reload();
			}}
		}}
	</script>

	</body>
</html>
"""



class EventHandleError (object):
	def __init__(self, event_name, event_seg_id, event_model_type_name, handler_seg_id, handler_model_type_name, exception, traceback):
		self.event_name = event_name
		self.event_seg_id = event_seg_id
		self.event_model_type_name = event_model_type_name
		self.handler_seg_id = handler_seg_id
		self.handler_model_type_name = handler_model_type_name
		self.err_html = present_exception.exception_to_html_src(exception, traceback)


	def to_message(self):
		return messages.error_handling_event_message(self.err_html, self.event_name, self.event_seg_id, self.event_model_type_name, self.handler_seg_id, self.handler_model_type_name)



class UnusedSegmentsError (Exception):
	def __init__(self, unused_segment_ids):
		super(UnusedSegmentsError, self).__init__('Segments created but not used: {0}'.format(unused_segment_ids))
		self.unused_segment_ids = unused_segment_ids



class DynamicDocumentPublicAPI (object):
	def __init__(self, document):
		self.__document = document


	def doc_js_eval(self, *expr):
		ex = []
		for x in expr:
			if isinstance(x, str)  or  isinstance(x, unicode):
				ex.append(x)
			else:
				ex.append(json.dumps(x))

		script = ''.join(ex)
		self.__document.queue_js_to_execute(script)
		# Ensure a refresh gets queued
		self.__document._notify_document_modified()


	def doc_js_function_call(self, js_fn_name, *json_args):
		call = [
			js_fn_name + '(',
			', '.join([json.dumps(a) for a in json_args]),
			');'
		]

		script = ''.join(call)
		self.__document.queue_js_to_execute(script)
		# Ensure a refresh gets queued
		self.__document._notify_document_modified()



class DynamicDocument (object):
	"""A dynamic web document, composed of segments.

	Create segments by calling the new_segment method. Remove them with remove_segment when you are done.

	You must create and set the root segment before using the document. Create using new_segment, then set the root_segment attribute.
	"""
	def __init__(self, service, session_id):
		self.__service = service
		self._session_id = session_id

		self.__public_api = DynamicDocumentPublicAPI(self)

		self._table = _SegmentTable(self)

		self.__queued_tasks = deque()

		self.__title = 'Ubiquitous Larch'

		# Global dependencies
		self.__global_deps_version = 0
		self.__global_deps = set()

		# Document event handlers
		self.__doc_event_handlers = []

		# Dependencies
		self.__dependencies = []
		self.__all_dependencies = set()

		# Document modification message and flag
		self.__document_modifications_message = None
		self.__document_modified = False

		# Queue of JS expressions that must be executed; will be put on the client in one batch later
		self.__js_queue = []
		self.__execute_js_message = None

		# The root segment
		self.__root_segment = None

		# Resources
		self.__rsc_id_counter = 1
		self.__rsc_id_to_rsc = {}
		self.__rsc_content_to_rsc = {}
		self.__modified_resources = set()
		self.__disposed_resources = set()

		# Threading lock, required for servers such as CherryPy
		self.__lock = None




	@property
	def service(self):
		return self.__service


	@property
	def public_api(self):
		return self.__public_api



	@property
	def title(self):
		return self.__title

	@title.setter
	def title(self, value):
		self.__title = value



	#
	#
	# Threads/locking
	#
	#

	def lock(self):
		if self.__lock is None:
			self.__lock = threading.Lock()
		self.__lock.acquire()

	def unlock(self):
		if self.__lock is not None:
			self.__lock.release()




	#
	#
	# Dependencies
	#
	#

	def add_dependency(self, dep):
		"""Register a dependency; such as a JS script or a CSS stylesheet

		dep - the dependency to register
		"""
		if not isinstance(dep, dependencies.DocumentDependency):
			raise TypeError, 'Dependencies must be an instance of DocumentDependency'

		if dep not in self.__all_dependencies:
			self.__all_dependencies.add(dep)

			for d in dep.dependencies:
				self.add_dependency(d)

			self.__dependencies.append(dep)







	#
	#
	# Segment creation and destruction
	#
	#


	def new_segment(self, content=None, desc=None, owner=None):
		"""
		Create a new segment

		:param content: an HTMLContent instance that contains the content of the segment that is to be created (or None, in which case you must initialise it by setting the segment's content attribute/property
		:param desc: a description string that is appended to the segment's ID. This is passed to the browser in order to allow you to figure out what e.g. seg27 is representing.
		:param owner: the owner of the segment
		:return: the new segment
		"""
		return self._table._new_segment(content, desc, owner)

	def remove_segment(self, segment):
		"""Remove a segment from the document. You should remove segments when you don't need them anymore.
		"""
		self._table._remove_segment(segment)




	#
	#
	# Resources
	#
	#

	def resource_for(self, rsc_data, context):
		"""Create a new resource

		rsc_data - A resource data object that provides:
			initialise(context, change_listener) and dispose(context) methods. These are called before the resource is first used and when it is no longer needed, respectively.
					The context parameter of these methods receives the value passed to context of this method
			data and mime_type attributes/properties: the data and its MIME type
		context - context data, used by the resource data object at initialisation and disposal time
		"""
		doc_rsc = self.__rsc_content_to_rsc.get(rsc_data)
		if doc_rsc is None:
			rsc_id = 'rsc{0}'.format(self.__rsc_id_counter)
			self.__rsc_id_counter += 1
			doc_rsc = DynamicResource(self, rsc_id, rsc_data)
			self.__rsc_id_to_rsc[rsc_id] = doc_rsc

		doc_rsc.ref(context)

		return doc_rsc


	def unref_resource(self, doc_rsc):
		if doc_rsc.unref() == 0:
			del self.__rsc_id_to_rsc[doc_rsc.id]


	def _resource_modified(self, rsc):
		"""Notify of resource modification
		"""
		self.__modified_resources.add(rsc.id)


	def _resouce_disposed(self, rsc):
		"""Notify of resource disposal
		"""
		self.__disposed_resources.add(rsc.id)


	def __resources_modified_message(self):
		if len(self.__modified_resources) > 0:
			rsc_mod_message = messages.resources_modified_message(self.__modified_resources - self.__disposed_resources)
			self.__modified_resources = set()
			return rsc_mod_message
		else:
			return None


	def __resources_disposed_message(self):
		if len(self.__disposed_resources) > 0:
			rsc_disp_message = messages.resources_disposed_message(self.__disposed_resources)
			self.__disposed_resources = set()
			return rsc_disp_message
		else:
			return None





	#
	#
	# Segment acquisition
	#
	#


	@property
	def root_segment(self):
		"""The root segment
		Defaults to None. You must set this before using the document.
		"""
		return self.__root_segment

	@root_segment.setter
	def root_segment(self, seg):
		if isinstance(seg, SegmentRef):
			seg = seg.segment
		self.__root_segment = seg



	#
	#
	# Events, tasks and synchronization
	#
	#

	def synchronize(self):
		"""Synchronise

		Executes all queued tasks, that were queued using the queue_task method.
		The resulting list of client messages is returned. These normally consist of modifications to perform to the browser DOM.
		"""
		# Execute queued tasks
		self.__execute_queued_tasks()

		# Build message list
		msg_list = []

		# Dependency message
		deps_list = []
		# Get new global dependencies
		if not global_dependencies.are_global_dependencies_up_to_date(self.__global_deps_version):
			global_deps = set()
			global_deps.update(global_dependencies.get_global_dependencies())
			deps_list.extend(global_deps.difference(self.__global_deps))
			self.__global_deps = global_deps
			self.__global_deps_version = global_dependencies.get_global_dependencies_version()

		deps_list.extend(self.__dependencies)
		self.__dependencies = []
		if len(deps_list) > 0:
			msg = messages.dependency_message([dep.to_html()   for dep in deps_list])
			msg_list.append(msg)

		# Document modifications message
		if self.__document_modifications_message is not None:
			msg_list.append(self.__document_modifications_message)
			self.__document_modifications_message = None

		# Execute JS message
		if self.__execute_js_message is not None:
			msg_list.append(self.__execute_js_message)
			self.__execute_js_message = None

		# Resource modification message
		rsc_mod_message = self.__resources_modified_message()
		if rsc_mod_message is not None:
			msg_list.append(rsc_mod_message)

		# Resource disposal message
		rsc_disp_message = self.__resources_disposed_message()
		if rsc_disp_message is not None:
			msg_list.append(rsc_disp_message)

		return msg_list



	def queue_task(self, task):
		"""Queue a task

		task must be callable
		"""
		self.__queued_tasks.append(task)



	# Event handling
	def handle_event(self, segment_id, event_name, ev_data):
		if segment_id is None:
			for handler_ev_name, handler_fn in self.__doc_event_handlers:
				if handler_ev_name == event_name:
					try:
						if handler_fn(self.__public_api, ev_data):
							return True
					except Exception, e:
						return EventHandleError(event_name, None, None, None, None, e, sys.exc_info()[2])
			return False
		else:
			try:
				event_segment = self._table[segment_id]
			except KeyError:
				return False

			segment = event_segment

			while segment is not None:
				try:
					if segment._handle_event(event_name, ev_data):
						return True
				except Exception, e:
					return EventHandleError(event_name, segment_id, type(event_segment.owner.model).__name__, segment.id, type(segment.owner.model).__name__, e, sys.exc_info()[2])
				segment = segment.parent
			return False


	def add_document_event_handler(self, event_name, event_response_function):
		self.__doc_event_handlers.append((event_name, event_response_function))


	# Resource retrieval
	def get_resource_data(self, rsc_id):
		try:
			rsc = self.__rsc_id_to_rsc[rsc_id]
		except KeyError:
			return None
		else:
			return rsc.data, rsc.mime_type






	def __execute_queued_tasks(self):
		while len(self.__queued_tasks) > 0:
			f = self.__queued_tasks.popleft()
			f()


	def queue_js_to_execute(self, js):
		self.__js_queue.append( js )


	def _notify_document_modified(self):
		# Segment changes notification. Called by _HtmlSegment.
		if not self.__document_modified:
			self.__document_modified = True
			self.queue_task(self.__refresh_document)


	def __refresh_document(self):
		# Refresh the document

		# Get the change set
		change_set = self._table._get_recent_changes()
		# Clear changes
		self._table._clear_changes()
		# Compose the modify document message
		self.__document_modifications_message = messages.modify_document_message(change_set.json())

		# Build the execute JS message
		if len(self.__js_queue) > 0:
			self.__execute_js_message = messages.execute_js_message('\n'.join(self.__js_queue))
			self.__js_queue = []

		self.__document_modified = False


	def page_html(self):
		if self.__root_segment is None:
			raise RuntimeError, 'Root segment has not been set.'
		root_content = self.__root_segment.reference()._complete_html()


		self.__global_deps.update(global_dependencies.get_global_dependencies())
		deps_list = list(self.__global_deps)  +  self.__dependencies
		self.__global_deps_version = global_dependencies.get_global_dependencies_version()

		dependency_tags = '\n'.join([dep.to_html()   for dep in deps_list])
		self.__dependencies = []

		initialisers = self._table._get_all_initialisers()
		initialisers_json_str = json.dumps(initialisers)

		if len(self.__js_queue) > 0:
			js_to_exec = '\n'.join(self.__js_queue)
			js_to_exec = '$(document).ready(function(){\n\t' + js_to_exec + '\n});'
			self.__js_queue = []
		else:
			js_to_exec = ''

		self._table._clear_changes()

		return _page_content.format(title=self.__title, session_id=self._session_id, dependency_tags=dependency_tags, content=root_content, init_script=js_to_exec, initialisers=initialisers_json_str)






class _ChangeSet (object):
	"""A change set

	Represents a set of DOM changes that must be applied by the client.
	"""
	def __init__(self, added_segs, removed_segs, modified_segs):
		"""Constructor

		added_segs - the list of new segments added
		removed_segs - the list of segments that were removed
		modified_segs - the list of modified segments

		Processes the changes, eliminating the added segments in the process; new segments should be children of modified segments, into which
		they are 'inlined'. By the time the inline process has finished, only removal and modification operations remain.
		"""
		self.__added_segs = added_segs

		self.__added_seg_to_html_bits = {}

		self.removed = [seg.id   for seg in removed_segs]
		self.modified = []
		self.initialise_scripts = []
		self.shutdown_scripts = []

		# Schedule the execution of the shutdown scripts of the segments that are being removed.
		for seg in removed_segs:
			shutdown_scripts = seg.get_shutdown_scripts()
			if shutdown_scripts is not None:
				self.shutdown_scripts.append((seg.id, shutdown_scripts))

		assert isinstance(self.__added_segs, set)
		while len(self.__added_segs) > 0:
			seg = added_segs.pop()
			initialise_scripts = seg.get_initialise_scripts()
			if initialise_scripts is not None:
				self.initialise_scripts.append((seg.id, initialise_scripts))
			items = []
			seg._build_inline_html(items, self.__resolve_reference)
			self.__added_seg_to_html_bits[seg] = items

		for seg in modified_segs:
			html = seg._inline_html(self.__resolve_reference)
			self.modified.append((seg.id, html))
			initialise_scripts = seg.get_initialise_scripts()
			if initialise_scripts is not None:
				self.initialise_scripts.append((seg.id, initialise_scripts))


		if len(self.__added_seg_to_html_bits) > 0  or  len(self.__added_segs) > 0:
			raise UnusedSegmentsError, set(self.__added_seg_to_html_bits.keys()).union(set(self.__added_segs))

		print 'CHANGES TO SEND: {0} removed, {1} modified, {2} initialise scripts, {3} shutdown scripts'.format(len(self.removed), len(self.modified), len(self.initialise_scripts), len(self.shutdown_scripts))




	def json(self):
		"""Generates a JSON object describing the changes
		"""
		return {'removed': self.removed, 'modified': self.modified, 'initialise_scripts': self.initialise_scripts, 'shutdown_scripts': self.shutdown_scripts}


	def __resolve_reference(self, items, seg):
		if seg in self.__added_seg_to_html_bits:
			html_bits = self.__added_seg_to_html_bits[seg]
			del self.__added_seg_to_html_bits[seg]
			items.extend(html_bits)
		elif seg in self.__added_segs:
			self.__added_segs.remove(seg)
			initialisers = seg.get_initialise_scripts()
			if initialisers is not None:
				self.initialise_scripts.append((seg.id, initialisers))
			seg._build_inline_html(items, self.__resolve_reference)
		else:
			items.append(seg._place_holder())




class _SegmentTable (object):
	def __init__(self, doc):
		self.__doc = doc

		self.__id_counter = 1
		self.__id_to_segment = {}

		self.__changes_added = set()
		self.__changes_removed = set()
		self.__changes_modified = set()



	def __getitem__(self, segment_id):
		return self.__id_to_segment[segment_id]



	def _clear_changes(self):
		self.__changes_added = set()
		self.__changes_removed = set()
		self.__changes_modified = set()


	def _get_recent_changes(self):
		return _ChangeSet(copy(self.__changes_added), copy(self.__changes_removed), copy(self.__changes_modified))


	def _get_all_initialisers(self):
		initialisers = []
		for segment in self.__id_to_segment.values():
			init_scripts = segment.get_initialise_scripts()
			if init_scripts is not None:
				initialisers.append((segment.id, init_scripts))
		return initialisers



	def _new_segment(self, content=None, desc=None, owner=None):
		desc_str = ('_' + desc)   if desc is not None   else ''
		seg_id = 'seg{0}{1}'.format(self.__id_counter, desc_str)
		self.__id_counter += 1
		seg = DynamicSegment(self.__doc, seg_id, content, owner)
		self.__id_to_segment[seg_id] = seg

		self.__changes_added.add(seg)

		self.__doc._notify_document_modified()

		return seg


	def _remove_segment(self, segment):
		del self.__id_to_segment[segment.id]

		if segment in self.__changes_added:
			self.__changes_added.remove(segment)
		else:
			self.__changes_removed.add(segment)

		self.__doc._notify_document_modified()


	def _segment_modified(self, segment, content):
		if segment not in self.__changes_added:
			self.__changes_modified.add(segment)

		self.__doc._notify_document_modified()





class DynamicResource (object):
	def __init__(self, doc, rsc_id, rsc_data):
		self.__doc = doc
		self.__rsc_id = rsc_id
		self.__rsc_data = rsc_data
		self.__context = None
		self.__ref_count = 0


	def ref(self, context):
		if self.__ref_count == 0:
			self.__context = context
			self.__rsc_data.initialise(context, self.__on_changed)
		self.__ref_count += 1
		return self.__ref_count

	def unref(self):
		self.__ref_count -= 1
		if self.__ref_count == 0:
			self.__rsc_data.dispose(self.__context)
			self.__doc._resouce_disposed(self)
		return self.__ref_count



	def __on_changed(self):
		self.__doc._resource_modified(self)


	@property
	def document(self):
		return self.__doc

	@property
	def id(self):
		return self.__rsc_id

	@property
	def data(self):
		return self.__rsc_data.data

	@property
	def mime_type(self):
		return self.__rsc_data.mime_type


	@property
	def url(self):
		return '/rsc?session_id={0}&rsc_id={1}'.format(self.__doc._session_id, self.__rsc_id)


	def client_side_js(self):
		return '(larch.__createResource("{0}", {1}))'.format(self.__rsc_id, json.dumps(self.url))