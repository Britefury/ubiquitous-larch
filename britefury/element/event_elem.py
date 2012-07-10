##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.element.element import Element
from britefury.element.abstract_event_elem import AbstractEventElement


class EventElement (AbstractEventElement):
	_unique_id_counter = 1


	def __init__(self, event_handler, content):
		super(EventElement, self).__init__(content)
		self.__event_handler = event_handler


	def handle_event(self, event_name, ev_data):
		return self.__event_handler(event_name, ev_data)


	def __html__(self):
		content_html = Element.html(self._content)
		return '<span class="__lch_event_elem" id="{0}">{1}</span>'.format(self.event_id, content_html)
