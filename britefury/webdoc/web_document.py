
from collections import deque
from britefury.message.execute_js_message import ExecuteJSMessage
from britefury.message.modify_document_message import ModifyDocumentMessage


_page_content = """
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

		self.__event_segments = []

		self.__session_id = session_id
		self.__stylesheet_names = stylesheet_names
		self.__script_names = script_names

		self.__js_queue = []

		self.__document_modified = False

		self._root_segment = None

		self._queue_js_to_execute('__larch.postDocumentEvent("initialise_document", {});')



	# Changes and segments

	def get_recent_changes(self):
		return self._table.get_recent_changes()

	def new_segment(self, content=None):
		return self._table.new_segment(content)

	def remove_segment(self, segment):
		self._table.remove_segment(segment)



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
	def _register_event_segment(self, element_id, element):
		self.__event_segments[element_id] = element


	def _unregister_event_segment(self, element_id):
		del self.__event_segments[element_id]


	def handle_event(self, segment_id, event_name, ev_data):
		if segment_id is None:
			return True
		else:
			segment = self.__event_segments[segment_id]
			while segment is not None:
				#if isinstance(segment, AbstractEventElement):
				if False:
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
		client_msg = ModifyDocumentMessage(changes)
		self.post_client_message(client_msg)
		self.__post_execute_js_messages()


	def html(self, root_content):
		stylesheet_tags = '\n'.join(['<link rel="stylesheet" type="text/css" href="{0}"/>'.format(stylesheet_name)   for stylesheet_name in self.__stylesheet_names])
		script_tags = '\n'.join(['<script type="text/javascript" src="{0}"></script>'.format(script_name)   for script_name in self.__script_names])
		if len(self.__js_queue) > 0:
			js_to_exec = '\n'.join(self.__js_queue)
			js_to_exec = '$(document).ready(function(){\n\t' + js_to_exec + '\n});'
			self.__js_queue = []
		else:
			js_to_exec = ''

		return _page_content.format(session_id=self.__session_id, stylesheet_tags=stylesheet_tags, script_tags=script_tags, content=root_content, init_script=js_to_exec)



class _SegmentTable (object):
	def __init__(self, doc):
		self.__doc = doc

		self.__id_counter = 1
		self.__id_to_segment = {}

		self.__changes_added = {}
		self.__changes_removed = set()
		self.__changes_modified = {}




	def get_recent_changes(self):
		changes = {'added': list(self.__changes_added.items()), 'removed': list(self.__changes_removed), 'modified': list(self.__changes_modified.items())}
		self.__changes_added = {}
		self.__changes_removed = set()
		self.__changes_modified = {}
		return changes



	def new_segment(self, content=None):
		id = 'seg{0}'.format(self.__id_counter)
		self.__id_counter += 1
		seg = _HtmlSegment(self.__doc, id, content)
		self.__id_to_segment[id] = seg

		self.__changes_added[id] = content.html()   if content is not None   else ''

		self.__doc._notify_document_modified()

		return seg


	def remove_segment(self, segment):
		id = segment.id
		del self.__id_to_segment[id]

		self.__changes_removed.add(id)

		self.__doc._notify_document_modified()


	def _segment_modified(self, segment, content):
		id = segment.id
		if id in self.__changes_added:
			self.__changes_added[id] = content.html()   if content is not None   else ''
		else:
			self.__changes_modified[segment.id] = content.html()   if content is not None   else ''

		self.__doc._notify_document_modified()







class _HtmlSegment (object):
	def __init__(self, doc, id, content=None):
		self.__doc = doc
		self.__id = id
		self.__content = content
		self.__parent = None


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
		self.__disconnect_children()
		self.__content = x
		self.__connect_children()
		self.__doc._table._segment_modified(self, x)


	def __connect_children(self):
		if self.__content is not None:
			for x in self.__content:
				if isinstance(x, _HtmlSegment):
					x.__parent = self

	def __disconnect_children(self):
		if self.__content is not None:
			for x in self.__content:
				if isinstance(x, _HtmlSegment) and x.__parent is self:
					x.__parent = None



	def reference(self):
		return SegmentRef(self)




class SegmentRef (object):
	def __init__(self, segment):
		self.__segment = segment
		self.__html = '<span class="__lch_placeholder">{0}</span>'.format(segment.id)


	@property
	def segment(self):
		return self.__segment

	def html(self):
		return self.__html



class HtmlContent (list):
	def __init__(self, contents):
		super(HtmlContent, self).__init__(contents)


	def html(self):
		xs = []
		for x in self:
			if isinstance(x, str)  or  isinstance(x, unicode):
				xs.append(x)
			else:
				xs.append(x.html())
		return ''.join(xs)