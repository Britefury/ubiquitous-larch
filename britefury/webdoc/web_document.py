
from collections import deque

import json

from copy import copy

from britefury.message.execute_js_message import ExecuteJSMessage
from britefury.message.modify_document_message import ModifyDocumentMessage


_page_content = """
<!doctype html>
<html>
	<head>
		<title>The Larch Environment (test)</title>
		<link rel="stylesheet" type="text/css" href="larch.css"/>
		{stylesheet_tags}

		<script type="text/javascript" src="larch_prelude.js"></script>
		<script type="text/javascript">
			<!--
			__larch.__session_id="{session_id}";
			// -->
		</script>
		<script type="text/javascript" src="jquery-1.7.2.js"></script>
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


class WebDocument (object):
	def __init__(self, session_id, stylesheet_names, script_names):
		self._table = _SegmentTable(self)

		self.__queued_tasks = deque()

		self.__client_message_queue = []

		self.__session_id = session_id
		self.__stylesheet_names = stylesheet_names
		self.__script_names = script_names

		self.__js_queue = []

		self.__document_modified = False

		self.__root_segment = None




	# Changes and segments

	def new_segment(self, content=None, desc=None):
		return self._table.new_segment(content, desc)

	def remove_segment(self, segment):
		self._table.remove_segment(segment)

	@property
	def root_segment(self):
		return self.__root_segment

	@root_segment.setter
	def root_segment(self, seg):
		if isinstance(seg, SegmentRef):
			seg = seg.segment
		self.__root_segment = seg



	# Queued tasks
	def queue(self, f):
		self.__queued_tasks.append(f)


	def execute_queued_tasks(self):
		while len(self.__queued_tasks) > 0:
			f = self.__queued_tasks.popleft()
			f()


	# Client message queue
	def post_client_message(self, cmd):
		self.__client_message_queue.append(cmd)

	def get_client_message_queue(self):
		return self.__client_message_queue

	def clear_client_message_queue(self):
		self.__client_message_queue = []


	def _queue_js_to_execute(self, js):
		self.__js_queue.append( js )


	def __post_execute_js_messages(self):
		if len(self.__js_queue) > 0:
			self.post_client_message(ExecuteJSMessage('\n'.join(self.__js_queue)))
			self.__js_queue = []



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
				if segment.handle_event(event_name, ev_data):
					return True
				segment = segment.parent
			return False


	# Segment changes notification
	def _notify_document_modified(self):
		if not self.__document_modified:
			self.__document_modified = True
			self.queue(self.__refresh_document)

	def __refresh_document(self):
		changes = self._table.get_recent_changes()
		self._table.clear_changes()
		client_msg = ModifyDocumentMessage(changes)
		self.post_client_message(client_msg)
		self.__post_execute_js_messages()
		self.__document_modified = False


	def page_html(self):
		root_content = self.__root_segment.reference().inline_html()

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

		return _page_content.format(session_id=self.__session_id, stylesheet_tags=stylesheet_tags, script_tags=script_tags, content=root_content, init_script=js_to_exec, initialisers=initialisers_json_str)






class _ChangeSet (object):
	def __init__(self, added_segs, removed_segs, modified_segs):
		self.__added_segs = added_segs

		self.__added_seg_to_html = {}

		self.removed = [seg.id   for seg in removed_segs]
		self.added = []
		self.modified = []
		self.initialisers = []

		assert isinstance(self.__added_segs, set)
		while len(self.__added_segs) > 0:
			seg = added_segs.pop()
			initialisers = seg.initialisers
			if initialisers is not None:
				self.initialisers.append((seg.id, initialisers))
			html = seg._inline_html(self.__resolve_reference)
			self.__added_seg_to_html[seg] = html

		for seg in modified_segs:
			html = seg._inline_html(self.__resolve_reference)
			self.modified.append((seg.id, html))
			initialisers = seg.initialisers
			if initialisers is not None:
				self.initialisers.append((seg.id, initialisers))

		assert len(self.__added_seg_to_html) == 0
		for seg, html in self.__added_seg_to_html.items():
			self.added.append((seg.id, html))

		print 'CHANGES TO SEND: {0} added, {1} removed, {2} modified, {3} initialisers'.format(len(self.added), len(self.removed), len(self.modified), len(self.initialisers))




	def json(self):
		return {'added': self.added, 'removed': self.removed, 'modified': self.modified, 'initialisers': self.initialisers}


	def __resolve_reference(self, seg):
		if seg in self.__added_seg_to_html:
			html = self.__added_seg_to_html[seg]
			del self.__added_seg_to_html[seg]
			return html
		elif seg in self.__added_segs:
			self.__added_segs.remove(seg)
			initialisers = seg.initialisers
			if initialisers is not None:
				self.initialisers.append((seg.id, initialisers))
			return seg._inline_html(self.__resolve_reference)
		else:
			return seg._place_holder()




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
			if segment.initialisers is not None:
				initialisers.append((segment.id, segment.initialisers))
		return initialisers



	def new_segment(self, content=None, desc=None):
		desc_str = ('_' + desc)   if desc is not None   else ''
		id = 'seg{0}{1}'.format(self.__id_counter, desc_str)
		self.__id_counter += 1
		seg = _HtmlSegment(self.__doc, id, content)
		self.__id_to_segment[id] = seg

		self.__changes_added.add(seg)

		self.__doc._notify_document_modified()

		return seg


	def remove_segment(self, segment):
		id = segment.id
		del self.__id_to_segment[id]

		self.__changes_removed.add(segment)

		self.__doc._notify_document_modified()


	def _segment_modified(self, segment, content):
		if segment not in self.__changes_added:
			self.__changes_modified.add(segment)

		self.__doc._notify_document_modified()







class _HtmlSegment (object):
	def __init__(self, doc, id, content=None):
		self.__doc = doc
		self.__id = id
		assert content is None  or  isinstance(content, HtmlContent)
		self.__content = content
		self.__parent = None
		self.__event_handlers = None
		self.__initialisers = None
		self.__connect_children()


	@property
	def id(self):
		return self.__id

	@property
	def parent(self):
		return self.__parent


	@property
	def content(self):
		return self.__content

	@content.setter
	def content(self, x):
		assert x is None  or  isinstance(x, HtmlContent)
		self.__disconnect_children()
		self.__content = x
		self.__connect_children()
		self.__doc._table._segment_modified(self, x)



	@property
	def initialisers(self):
		return self.__initialisers



	# Event handling
	def add_event_handler(self, handler):
		if self.__event_handlers is None:
			self.__event_handlers = []
		self.__event_handlers.append(handler)


	def handle_event(self, event_name, ev_data):
		if self.__event_handlers is not None:
			for handler in self.__event_handlers:
				if handler(event_name, ev_data):
					return True
		return False


	# Initialisation
	def add_initialiser(self, initialiser):
		if self.__initialisers is None:
			self.__initialisers = []
		self.__initialisers.append(initialiser)



	# HTML generation
	def html(self, ref_resolver=None):
		return self.__content.html(ref_resolver)   if self.__content is not None   else ''


	def _place_holder(self):
		return '<span class="__lch_seg_placeholder">{0}</span>'.format(self.__id)

	def _inline_html(self, ref_resolver):
		html = self.__content.html(ref_resolver)   if self.__content is not None   else ''
		return '<span class="__lch_seg_begin">{0}</span>{1}<span class="__lch_seg_end">{0}</span>'.format(self.__id, html)



	def __connect_children(self):
		if self.__content is not None:
			for x in self.__content:
				if isinstance(x, SegmentRef):
					x = x.segment
				if isinstance(x, _HtmlSegment):
					x.__parent = self

	def __disconnect_children(self):
		if self.__content is not None:
			for x in self.__content:
				if isinstance(x, SegmentRef):
					x = x.segment
				if isinstance(x, _HtmlSegment) and x.__parent is self:
					x.__parent = None



	def reference(self):
		return SegmentRef(self)




class SegmentRef (object):
	def __init__(self, segment):
		assert isinstance(segment, _HtmlSegment)
		self.__segment = segment


	@property
	def segment(self):
		return self.__segment

	def html(self, ref_resolver=None):
		if ref_resolver is not None:
			return ref_resolver(self.__segment)
		else:
			return self.__segment._place_holder()


	def inline_html(self):
		return self.html(self.__resolve_inline)


	def __resolve_inline(self, seg):
		return seg._inline_html(self.__resolve_inline)



class HtmlContent (list):
	def __init__(self, contents):
		for x in contents:
			assert isinstance(x, str)  or  isinstance(x, unicode)  or  isinstance(x, SegmentRef)  or  isinstance(x, HtmlContent)
		super(HtmlContent, self).__init__(contents)


	def html(self, ref_resolver=None):
		xs = []
		for x in self:
			if isinstance(x, str)  or  isinstance(x, unicode):
				xs.append(x)
			else:
				xs.append(x.html(ref_resolver))
		return ''.join(xs)