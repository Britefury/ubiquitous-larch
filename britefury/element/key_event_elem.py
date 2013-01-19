##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json
from britefury.element.element import Element
from britefury.element.abstract_event_elem import AbstractEventElement



class Key (object):
	KEY_DOWN = 'KEY_DOWN'
	KEY_UP = 'KEY_UP'
	KEY_PRESS = 'KEY_PRESS'


	def __init__(self, event_type, key_code, alt=None, ctrl=None, shift=None, meta=None):
		if event_type != self.KEY_DOWN  and  event_type != self.KEY_UP  and  event_type != self.KEY_PRESS:
			raise ValueError, 'invalid event_type; should be KEY_DOWN, KEY_UP, or KEY_PRESS'
		self.__event_type = event_type

		if isinstance(key_code, str)  or  isinstance(key_code, unicode):
			key_code = ord(key_code)
		elif isinstance(key_code, int)  or  key_code is None:
			pass
		else:
			raise TypeError, 'invalid key_code type; should be string, integer or None'
		self.__key_code = key_code

		self.__alt = alt
		self.__ctrl = ctrl
		self.__shift = shift
		self.__meta = meta


	@property
	def event_type(self):
		return self.__event_type

	@property
	def key_code(self):
		return self.__key_code

	@property
	def key_char(self):
		return chr(self.__key_code)


	@property
	def alt(self):
		return self.__alt

	@property
	def ctrl(self):
		return self.__ctrl

	@property
	def shift(self):
		return self.__shift

	@property
	def meta(self):
		return self.__meta


	def matches(self, filter):
		return (self.__event_type == filter.__event_type)  and \
		       (self.__key_code == filter.__key_code  or  filter.__key_code is None)  and \
		       (self.__alt == filter.__alt  or  filter.__alt is None)  and \
		       (self.__ctrl == filter.__ctrl  or  filter.__ctrl is None)  and \
		       (self.__shift == filter.__shift  or  filter.__shift is None)  and \
		       (self.__meta == filter.__meta  or  filter.__meta is None)


	def __to_json__(self):
		k = {'event_type' : self.__event_type}

		if self.__key_code is not None:
			k['keyCode'] = self.__key_code

		if self.__alt is not None:
			k['altKey'] = 1   if self.__alt   else 0
		if self.__ctrl is not None:
			k['ctrlKey'] = 1   if self.__ctrl   else 0
		if self.__shift is not None:
			k['shiftKey'] = 1   if self.__shift   else 0
		if self.__meta is not None:
			k['metaKey'] = 1   if self.__meta   else 0

		return k


	@staticmethod
	def __from_json__(event_type, json):
		key_code = json.get('keyCode', 0)
		alt = json.get('altKey') == 1
		ctrl = json.get('ctrlKey') == 1
		shift = json.get('shiftKey') == 1
		meta = json.get('metaKey') == 1
		return Key(event_type, key_code, alt, ctrl, shift, meta)


	@staticmethod
	def __from_keydown_json__(json):
		return Key.__from_json__(Key.KEY_DOWN, json)


	@staticmethod
	def __from_keyup_json__(json):
		return Key.__from_json__(Key.KEY_UP, json)


	@staticmethod
	def __from_keypress_json__(json):
		return Key.__from_json__(Key.KEY_PRESS, json)





class KeyEventElement (AbstractEventElement):
	def __init__(self, content, keys_and_handlers):
		super(KeyEventElement, self).__init__(content)

		self.__keydown = [k   for k in keys_and_handlers   if k[0].event_type == Key.KEY_DOWN]
		self.__keyup = [k   for k in keys_and_handlers   if k[0].event_type == Key.KEY_DOWN]
		self.__keypress = [k   for k in keys_and_handlers   if k[0].event_type == Key.KEY_DOWN]

		self.__keydown_json_str = json.dumps([k[0].__to_json__()   for k in self.__keydown])
		self.__keyup_json_str = json.dumps([k[0].__to_json__()   for k in self.__keyup])
		self.__keypress_json_str = json.dumps([k[0].__to_json__()   for k in self.__keypress])


	def handle_event(self, event_name, ev_data):
		if event_name == 'keydown':
			ev_key = Key.__from_keydown_json__(ev_data)
			keys_and_handlers = self.__keydown
		elif event_name == 'keyup':
			ev_key = Key.__from_keyup_json__(ev_data)
			keys_and_handlers = self.__keyup
		elif event_name == 'keypress':
			ev_key = Key.__from_keypress_json__(ev_data)
			keys_and_handlers = self.__keypress
		else:
			return False

		for key, handler in keys_and_handlers:
			if ev_key.matches(key):
				return handler(ev_key)
				break
		return False



	def __html__(self, level):
		content_html = Element.html(self._content)
		keydown_json = self.__keydown_json_str.replace('"', '\'')
		keyup_json = self.__keyup_json_str.replace('"', '\'')
		keypress_json = self.__keypress_json_str.replace('"', '\'')
		a = {'class' : '__lch_event_elem',
		     'id': str(self.element_id),
		     'onkeydown': 'return __larch.__onkeydown(event, {0});'.format(keydown_json),
		     'onkeyup': 'return __larch.__onkeyup(event, {0});'.format(keyup_json),
		     'onkeypress': 'return __larch.__onkeypress(event, {0});'.format(keypress_json)}

		return self._container(level, a, self._content.__html__(level))
