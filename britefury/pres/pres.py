##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json

from britefury.webdoc.web_document import HtmlContent
from britefury.pres.presctx import PresentationContext
from britefury.pres.key_event import Key



class Pres (object):
	def build(self, pres_ctx):
		raise NotImplementedError, 'abstract'


	def with_event_handler(self, event_filter_or_handler, event_handler=None):
		if event_handler is None:
			return EventSource(event_filter_or_handler, self)
		else:
			if isinstance(event_filter_or_handler, str)  or  isinstance(event_filter_or_handler, unicode):
				def _handle(event_name, ev_data):
					if event_name == event_filter_or_handler:
						return event_handler(event_name, ev_data)
					else:
						return False
				return EventSource(_handle, self)
			else:
				raise TypeError, 'filter should be string or unicode'


	def with_key_handler(self, keys, handler):
		keys_and_handlers = [(key, handler)   for key in keys]
		return KeyEventSource(keys_and_handlers, self)


	def call_js(self, js_fun_name):
		return JSCall([js_fun_name], self)



	@staticmethod
	def map_build(pres_ctx, xs):
		return [x.build(pres_ctx)   for x in xs]


	@staticmethod
	def coerce(x):
		if x is None:
			return None
		elif isinstance(x, Pres):
			return x
		else:
			return InnerFragment(x)


	@staticmethod
	def coerce_not_none(x):
		if x is None:
			return InnerFragment(None)
		elif isinstance(x, Pres):
			return x
		else:
			return InnerFragment(x)


	@staticmethod
	def map_coerce(xs):
		return [Pres.coerce(x)   for x in xs]

	@staticmethod
	def map_coerce_not_none(xs):
		return [Pres.coerce_not_none(x)   for x in xs]



class CompositePres (Pres):
	def build(self, pres_ctx):
		return self.pres(pres_ctx).build(pres_ctx)

	def pres(self, pres_ctx):
		raise NotImplementedError, 'abstract'


class ApplyPerspective (Pres):
	def __init__(self, perspective, child):
		self.__perspective = perspective
		self.__child = Pres.coerce_not_none(child)


	def build(self, pres_ctx):
		return self.__child.build(PresentationContext(pres_ctx.fragment_view, self.__perspective, pres_ctx.inherited_state))



class InnerFragment (Pres):
	def __init__(self, model):
		self.__model = model


	def build(self, pres_ctx):
		fragment_view = pres_ctx.fragment_view
		inherited_state = pres_ctx.inherited_state
		return fragment_view.present_inner_fragment(self.__model, pres_ctx.perspective, inherited_state)




class SubSegmentPres (Pres):
	def __init__(self, child):
		self.__child = Pres.coerce_not_none(child)



	def initialise_segment(self, seg, pres_ctx):
		pass

	def build(self, pres_ctx):
		seg = pres_ctx.fragment_view.create_sub_segment(self.__child.build(pres_ctx))
		self.initialise_segment(seg, pres_ctx)
		return HtmlContent([seg.reference()])





class EventSource (SubSegmentPres):
	def __init__(self, event_handler, child):
		super(EventSource, self).__init__(child)
		self.__event_handler = event_handler


	def initialise_segment(self, seg, pres_ctx):
		seg.add_event_handler(self.__event_handler)




class JSCall (Pres):
	def __init__(self, js_fn_names, child):
		self.__js_fn_names = js_fn_names
		self.__child = Pres.coerce_not_none(child)


	def call_js(self, js_fun_name):
		return JSCall(self.__js_fn_names + [js_fun_name], self.__child)


	def build(self, pres_ctx):
		return self.__child.build(pres_ctx)
#		return JSElement(self.__js_fn_names, self.__child.build(pres_ctx))



class KeyEventSource (EventSource):
	def __init__(self, keys_and_handlers, child):
		super(KeyEventSource, self).__init__(self.__handle_key_event, child)

		self.__keys_and_handlers = keys_and_handlers

		self.__keydown = [k   for k in keys_and_handlers   if k[0].event_type == Key.KEY_DOWN]
		self.__keyup = [k   for k in keys_and_handlers   if k[0].event_type == Key.KEY_DOWN]
		self.__keypress = [k   for k in keys_and_handlers   if k[0].event_type == Key.KEY_DOWN]

		self.__keydown_json_str = json.dumps([k[0].__to_json__()   for k in self.__keydown])
		self.__keyup_json_str = json.dumps([k[0].__to_json__()   for k in self.__keyup])
		self.__keypress_json_str = json.dumps([k[0].__to_json__()   for k in self.__keypress])



	def with_key_handler(self, keys, handler):
		keys_and_handlers = [(key, handler)   for key in keys]
		return KeyEventSource(self.__keys_and_handlers + keys_and_handlers, self._child)


	def __handle_key_event(self, event_name, ev_data):
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

		return False



	def initialise_segment(self, seg, pres_ctx):
		super(KeyEventSource, self).initialise_segment(seg, pres_ctx)
		keydown_json = self.__keydown_json_str.replace('"', '\'')
		keyup_json = self.__keyup_json_str.replace('"', '\'')
		keypress_json = self.__keypress_json_str.replace('"', '\'')
		seg.add_initialiser('node.onkeydown = function(event) {{__larch.__onkeydown(event, {0});}}'.format(keydown_json))
		seg.add_initialiser('node.onkeyup = function(event) {{__larch.__onkeyup(event, {0});}}'.format(keyup_json))
		seg.add_initialiser('node.onkeypress = function(event) {{__larch.__onkeypress(event, {0});}}'.format(keypress_json))



