##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import threading

from collections import deque

import json

from copy import copy

from britefury.message.execute_js_message import ExecuteJSMessage
from britefury.message.modify_document_message import ModifyDocumentMessage

from britefury.dynamicsegments.segment import DynamicSegment, SegmentRef


_page_content = """
<!doctype html>
<html>
	<head>
		<title>The Larch Environment (test)</title>
		<link rel="stylesheet" type="text/css" href="jquery-ui-1.10.1.custom.min.css"/>
		<link rel="stylesheet" type="text/css" href="larch.css"/>
		<link rel="stylesheet" type="text/css" href="python.css"/>
		<link rel="stylesheet" type="text/css" href="console.css"/>
		<link rel="stylesheet" type="text/css" href="worksheet.css"/>
		{stylesheet_tags}

		<script type="text/javascript" src="larch_prelude.js"></script>
		<script type="text/javascript">
			<!--
			__larch.__session_id="{session_id}";
			// -->
		</script>
		<script type="text/javascript" src="jquery-1.9.1.js"></script>
		<script type="text/javascript" src="jquery-ui-1.10.1.custom.min.js"></script>
		<script type="text/javascript" src="json2.js"></script>
		<script type="text/javascript" src="larch.js"></script>
		{script_tags}
		<script type="text/javascript">
			<!--
			$(document).ready(function(){{__larch.__onDocumentReady({initialisers});}});
			{init_script}
			// -->
		</script>
	</head>

	<body>
	{content}
	</body>
</html>
"""


class DynamicDocument (object):
	"""A dynamic web document, composed of segments.

	Create segments by calling the new_segment method. Remove them with remove_segment when you are done.

	You must create and set the root segment before using the document. Create using new_segment, then set the root_segment attribute.
	"""
	def __init__(self, session_id):
		self._table = _SegmentTable(self)

		self.__queued_tasks = deque()

		self.__client_message_queue = []

		self._session_id = session_id
		self.__stylesheet_names = []
		self.__script_names = []

		self.__js_queue = []

		self.__document_modified = False

		self.__root_segment = None


		self.__rsc_id_counter = 1
		self.__rsc_id_to_rsc = {}
		self.__rsc_content_to_rsc = {}


		self.__lock = None



	def add_stylesheets(self, names):
		self.__stylesheet_names.extend(names)



	def add_js_scripts(self, names):
		self.__script_names.extend(names)




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
	# Segment creation and destruction
	#
	#


	def new_segment(self, content=None, desc=None):
		"""Create a new segment

		content - an HTMLContent instance that contains the content of the segment that is to be created (or None, in which case you must initialise it by setting the segment's content attribute/property
		desc - a description string that is appended to the segment's ID. This is passed to the browser in order to allow you to figure out what e.g. seg27 is representing.
		"""
		return self._table.new_segment(content, desc)

	def remove_segment(self, segment):
		"""Remove a segment from the document. You should remove segments when you don't need them anymore.
		"""
		self._table.remove_segment(segment)




	#
	#
	# Resources
	#
	#

	def resource_for(self, data_fn, mime_type):
		"""Create a new resource

		data_fn - function that returns the resource's content
		mime_type - the MIME type
		"""
		key = data_fn, mime_type
		rsc = self.__rsc_content_to_rsc.get(key)
		if rsc is None:
			rsc_id = 'rsc{0}'.format(self.__rsc_id_counter)
			self.__rsc_id_counter += 1
			rsc = DynamicResource(self, rsc_id, data_fn, mime_type)
			self.__rsc_id_to_rsc[rsc_id] = rsc

		rsc.ref()

		return rsc


	def unref_resource(self, rsc):
		if rsc.unref() == 0:
			del self.__rsc_id_to_rsc[rsc.id]




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
		self.__execute_queued_tasks()
		# Take a copy of the client message queue before clearing it
		client_messages = self.__client_message_queue
		self.__client_message_queue = []
		return client_messages



	def queue_task(self, task):
		"""Queue a task

		task must be callable
		"""
		self.__queued_tasks.append(task)



	# Event handling
	def handle_event(self, segment_id, event_name, ev_data):
		if segment_id is None:
			return True
		else:
			try:
				segment = self._table[segment_id]
			except KeyError:
				return False

			while segment is not None:
				if segment._handle_event(event_name, ev_data):
					return True
				segment = segment.parent
			return False


	# Resource retrieval
	def get_resource_data(self, rsc_id):
		rsc = self.__rsc_id_to_rsc[rsc_id]
		return rsc.data, rsc.mime_type






	def __execute_queued_tasks(self):
		while len(self.__queued_tasks) > 0:
			f = self.__queued_tasks.popleft()
			f()


	def __queue_client_message(self, cmd):
		# Post a message into the client message queue
		self.__client_message_queue.append(cmd)



	def _queue_js_to_execute(self, js):
		self.__js_queue.append( js )


	def __post_execute_js_messages(self):
		if len(self.__js_queue) > 0:
			self.__queue_client_message(ExecuteJSMessage('\n'.join(self.__js_queue)))
			self.__js_queue = []



	def _notify_document_modified(self):
		# Segment changes notification. Called by _HtmlSegment.
		if not self.__document_modified:
			self.__document_modified = True
			self.queue_task(self.__refresh_document)


	def __refresh_document(self):
		# Refresh the document

		# Get the change set
		changes = self._table.get_recent_changes()
		# Clear changes
		self._table.clear_changes()
		# Compose the modify document message
		client_msg = ModifyDocumentMessage(changes)
		# Post to the client
		self.__queue_client_message(client_msg)
		self.__post_execute_js_messages()
		self.__document_modified = False


	def page_html(self):
		if self.__root_segment is None:
			raise RuntimeError, 'Root segment has not been set.'
		root_content = self.__root_segment.reference()._complete_html()

		stylesheet_tags = '\n'.join(['<link rel="stylesheet" type="text/css" href="{0}"/>'.format(stylesheet_name)   for stylesheet_name in self.__stylesheet_names])
		script_tags = '\n'.join(['<script type="text/javascript" src="{0}"></script>'.format(script_name)   for script_name in self.__script_names])

		initialisers = self._table.get_all_initialisers()
		initialisers_json_str = json.dumps(initialisers)

		if len(self.__js_queue) > 0:
			js_to_exec = '\n'.join(self.__js_queue)
			js_to_exec = '$(document).ready(function(){\n\t' + js_to_exec + '\n});'
			self.__js_queue = []
		else:
			js_to_exec = ''

		self._table.clear_changes()

		return _page_content.format(session_id=self._session_id, stylesheet_tags=stylesheet_tags, script_tags=script_tags, content=root_content, init_script=js_to_exec, initialisers=initialisers_json_str)






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
		self.initialisers = []

		assert isinstance(self.__added_segs, set)
		while len(self.__added_segs) > 0:
			seg = added_segs.pop()
			initialisers = seg.get_initialisers()
			if initialisers is not None:
				self.initialisers.append((seg.id, initialisers))
			items = []
			html = seg._build_inline_html(items, self.__resolve_reference)
			self.__added_seg_to_html_bits[seg] = items

		for seg in modified_segs:
			html = seg._inline_html(self.__resolve_reference)
			self.modified.append((seg.id, html))
			initialisers = seg.get_initialisers()
			if initialisers is not None:
				self.initialisers.append((seg.id, initialisers))

		assert len(self.__added_seg_to_html_bits) == 0
		assert len(self.__added_segs) == 0

		print 'CHANGES TO SEND: {0} removed, {1} modified, {2} initialisers'.format(len(self.removed), len(self.modified), len(self.initialisers))




	def json(self):
		"""Generates a JSON object describing the changes
		"""
		return {'removed': self.removed, 'modified': self.modified, 'initialisers': self.initialisers}


	def __resolve_reference(self, items, seg):
		if seg in self.__added_seg_to_html_bits:
			html_bits = self.__added_seg_to_html_bits[seg]
			del self.__added_seg_to_html_bits[seg]
			items.extend(html_bits)
		elif seg in self.__added_segs:
			self.__added_segs.remove(seg)
			initialisers = seg.get_initialisers()
			if initialisers is not None:
				self.initialisers.append((seg.id, initialisers))
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



	def clear_changes(self):
		self.__changes_added = set()
		self.__changes_removed = set()
		self.__changes_modified = set()


	def get_recent_changes(self):
		changes = _ChangeSet(copy(self.__changes_added), copy(self.__changes_removed), copy(self.__changes_modified))

		return changes.json()


	def get_all_initialisers(self):
		initialisers = []
		for segment in self.__id_to_segment.values():
			if segment.get_initialisers() is not None:
				initialisers.append((segment.id, segment.get_initialisers()))
		return initialisers



	def new_segment(self, content=None, desc=None):
		desc_str = ('_' + desc)   if desc is not None   else ''
		seg_id = 'seg{0}{1}'.format(self.__id_counter, desc_str)
		self.__id_counter += 1
		seg = DynamicSegment(self.__doc, seg_id, content)
		self.__id_to_segment[seg_id] = seg

		self.__changes_added.add(seg)

		self.__doc._notify_document_modified()

		return seg


	def remove_segment(self, segment):
		del self.__id_to_segment[segment.id]

		self.__changes_removed.add(segment)

		self.__doc._notify_document_modified()


	def _segment_modified(self, segment, content):
		if segment not in self.__changes_added:
			self.__changes_modified.add(segment)

		self.__doc._notify_document_modified()





class DynamicResource (object):
	def __init__(self, doc, rsc_id, data_fn, mime_type):
		self.__doc = doc
		self.__rsc_id = rsc_id
		self.__data_fn = data_fn
		self.__mime_type = mime_type
		self.__ref_count = 0


	def ref(self):
		self.__ref_count += 1
		return self.__ref_count

	def unref(self):
		self.__ref_count -= 1
		return self.__ref_count


	@property
	def document(self):
		return self.__doc

	@property
	def id(self):
		return self.__rsc_id

	@property
	def data(self):
		return self.__data_fn()

	@property
	def mime_type(self):
		return self.__mime_type


	@property
	def url(self):
		return 'rsc?session_id={0}&rsc_id={1}'.format(self.__doc._session_id, self.__rsc_id)