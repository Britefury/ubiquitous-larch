##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json



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
		return (self.__event_type == filter.__event_type)  and\
		       (self.__key_code == filter.__key_code  or  filter.__key_code is None)  and\
		       (self.__alt == filter.__alt  or  filter.__alt is None)  and\
		       (self.__ctrl == filter.__ctrl  or  filter.__ctrl is None)  and\
		       (self.__shift == filter.__shift  or  filter.__shift is None)  and\
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




