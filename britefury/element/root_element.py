##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************
from collections import deque

from britefury.element.element import Element


_page_content_pre = """
<html>
	<head>
		<title>The Larch Environment (test)</title>
		<link rel="stylesheet" type="text/css" href="larch.css"/>
		<script type="text/javascript" src="jquery-1.7.2.js"></script>
		<script type="text/javascript" src="larch.js"></script>
	</head>

	<body>
"""


_page_content_post = """
	</body>
</html>
"""

class RootElement (Element):
	def __init__(self):
		super(RootElement, self).__init__()
		self.__content = None
		self._parent = None
		self._root_element = self

		self.__event_queue = deque()

		self.__fragments_to_refresh = set()

		self.__client_command_queue = []



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
		self.__event_queue.append(f)


	def execute_queued_events(self):
		while len(self.__event_queue) > 0:
			f = self.__event_queue.popleft()
			f()



	def post_client_command(self, cmd):
		self.__client_command_queue.append(cmd)


	def get_client_command_queue(self):
		return self.__client_command_queue

	def clear_client_command_queue(self):
		self.__client_command_queue = []


	def _notify_fragment_modified(self, fragment):
		if len(self.__fragments_to_refresh) == 0:
			self.queue(self.__refresh_fragments)

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
			client_cmd = {'cmd_type' : 'replace_fragment', 'frag_id' : str(fragment.fragment_id), 'frag_content' : html}
			self.post_client_command(client_cmd)
		self.__fragments_to_refresh.clear()


	def __html__(self):
		return _page_content_pre + Element.html(self.__content) + _page_content_post
