##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json

from britefury.element.element import Element
from britefury.element.abstract_event_elem import AbstractEventElement


class EventElement (AbstractEventElement):
	_unique_id_counter = 1


	def __init__(self, event_handler, content):
		super(EventElement, self).__init__(content)
		self.__event_handler = event_handler


	def handle_event(self, event_name, ev_data):
		return self.__event_handler(event_name, ev_data)


	def __html__(self, level):
		return self._container(level, {'class': '__lch_event_elem', 'id': self.element_id}, self._content.__html__(level))



def post_event_js_code(event_name, event_json={}, event_source_js='this'):
	return '__larch.postEvent({0},\'{1}\', {2});'.format(event_source_js, event_name, json.dumps(event_json))

def post_event_js_code_for_handler(event_name, event_json={}, event_source_js='this'):
	return 'javascript:__larch.postEvent({0},\'{1}\', {2});'.format(event_source_js, event_name, json.dumps(event_json))
