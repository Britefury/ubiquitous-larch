##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.webdoc.web_document import HtmlContent
from britefury.pres.presctx import PresentationContext



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


	def build(self, pres_ctx):
		seg = pres_ctx.fragment_view.create_sub_segment(self.__child.build(pres_ctx))
		return HtmlContent([seg.reference()])





class EventSource (Pres):
	def __init__(self, event_handler, child):
		self.__event_handler = event_handler
		self.__child = Pres.coerce_not_none(child)


	def build(self, pres_ctx):
		return self.__child.build(pres_ctx)
#		return EventElement(self.__event_handler, self.__child.build(pres_ctx))



class KeyEventSource (Pres):
	def __init__(self, keys_and_handlers, child):
		self.__keys_and_handlers = keys_and_handlers
		self.__child = Pres.coerce_not_none(child)


	def with_key_handler(self, keys, handler):
		keys_and_handlers = [(key, handler)   for key in keys]
		return KeyEventSource(self.__keys_and_handlers + keys_and_handlers, self.__child)


	def build(self, pres_ctx):
		return self.__child.build(pres_ctx)
#		return KeyEventElement(self.__child.build(pres_ctx), self.__keys_and_handlers)



class JSCall (Pres):
	def __init__(self, js_fn_names, child):
		self.__js_fn_names = js_fn_names
		self.__child = Pres.coerce_not_none(child)


	def call_js(self, js_fun_name):
		return JSCall(self.__js_fn_names + [js_fun_name], self.__child)


	def build(self, pres_ctx):
		return self.__child.build(pres_ctx)
#		return JSElement(self.__js_fn_names, self.__child.build(pres_ctx))