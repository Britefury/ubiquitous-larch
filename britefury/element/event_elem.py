##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************
from britefury.element.element import Element


class EventElement (Element):
	_unique_id_counter = 1


	def __init__(self, event_handler, content):
		super(EventElement, self).__init__()
		self.__event_handler = event_handler

		self.__content = content
		if self.__content is not None:
			self.__content.parent = self

		self.__unique_id = EventElement._unique_id_counter
		EventElement._unique_id_counter += 1


	@property
	def event_id(self):
		return 'lch_event_' + str(self.__unique_id)


	def handle_event(self, event_name, ev_data):
		self.__event_handler(event_name, ev_data)



	@property
	def content(self):
		return self.__content


	@property
	def children(self):
		yield self.__content


	def _set_root_element(self, root):
		if self._root_element is not None:
			self._root_element._unregister_event_element(self.event_id)
		super(EventElement, self)._set_root_element(root)
		if self._root_element is not None:
			self._root_element._register_event_element(self.event_id, self)


	def __html__(self):
		content_html = Element.html(self.__content)
		return '<span class="__lch_event_elem" id="{0}">{1}</span>'.format(self.event_id, content_html)


	def _content_html(self):
		return Element.html(self.__content)