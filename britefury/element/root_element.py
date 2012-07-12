##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from collections import deque

from britefury.element.element import Element
from britefury.element.abstract_event_elem import AbstractEventElement
from britefury.message.replace_fragment_message import ReplaceFragmentMessage
from britefury.message.execute_js_message import ExecuteJSMessage


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


class RootElement (Element):
	def __init__(self, session_id, stylesheet_names, script_names):
		super(RootElement, self).__init__()
		self.__content = None
		self._parent = None
		self._root_element = self

		self.__session_id = session_id
		self.__stylesheet_names = stylesheet_names
		self.__script_names = script_names

		self.__queued_tasks = deque()

		self.__fragments_to_refresh = set()

		self.__js_queue = []

		self.__client_message_queue = []

		self.__event_elements = {}



	@property
	def content(self):
		return self.__content

	@content.setter
	def content(self, c):
		self.__content = c
		c.parent = self


	@property
	def children(self):
		yield self.__content



	def queue(self, f):
		self.__queued_tasks.append(f)


	def execute_queued_tasks(self):
		while len(self.__queued_tasks) > 0:
			f = self.__queued_tasks.popleft()
			f()



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



	def _register_event_element(self, element_id, element):
		self.__event_elements[element_id] = element


	def _unregister_event_element(self, element_id):
		del self.__event_elements[element_id]


	def handle_event(self, element_id, event_name, ev_data):
		element = self.__event_elements[element_id]
		while element is not None:
			if isinstance(element, AbstractEventElement):
				if element.handle_event(event_name, ev_data):
					return True
			element = element.parent
		return False



	def _notify_fragment_modified(self, fragment):
		if len(self.__fragments_to_refresh) == 0:
			self.queue(self.__refresh_fragments)

		# TODO: Not likely to be efficient in any way....
		descendants = fragment.ancestor_of_elements(self.__fragments_to_refresh)
		if len(descendants) > 0:
			self.__fragments_to_refresh.difference_update(descendants)
			self.__fragments_to_refresh.add(fragment)
		else:
			if not fragment.descendant_of_one_of(self.__fragments_to_refresh):
				self.__fragments_to_refresh.add(fragment)


	def __refresh_fragments(self):
		for fragment in self.__fragments_to_refresh:
			html = fragment._content_html()
			client_msg = ReplaceFragmentMessage(fragment.fragment_id, html)
			self.post_client_message(client_msg)
		self.__fragments_to_refresh.clear()
		self.__post_execute_js_messages()



	def __html__(self):
		stylesheet_tags = '\n'.join(['<link rel="stylesheet" type="text/css" href="{0}"/>'.format(stylesheet_name)   for stylesheet_name in self.__stylesheet_names])
		script_tags = '\n'.join(['<script type="text/javascript" src="{0}"></script>'.format(script_name)   for script_name in self.__script_names])
		if len(self.__js_queue) > 0:
			js_to_exec = '\n'.join(self.__js_queue)
			js_to_exec = '$(document).ready(function(){\n\t' + js_to_exec + '\n});'
			self.__js_queue = []
		else:
			js_to_exec = ''

		return _page_content.format(session_id=self.__session_id, stylesheet_tags=stylesheet_tags, script_tags=script_tags, content=Element.html(self.__content), init_script=js_to_exec)
