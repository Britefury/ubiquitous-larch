##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json

from britefury.dynamicpage.segment import HtmlContent
from britefury.dynamicpage import dependencies
from britefury.pres.presctx import PresentationContext
from britefury.pres.key_event import KeyAction
from britefury.pres import js



_ext_dependencies = {}


_node_js = js.JSName('node')

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


	def js_eval(self, expr):
		if isinstance(expr, str)  or  isinstance(expr, unicode):
			expr = js.JSExprSrc(expr)
		elif not isinstance(expr, js.JS):
			raise TypeError, 'Javascript expression must be a string or a JS object'
		return JSInitEval(self, expr)

	def js_function_call(self, js_fn_name, *args):
		return JSInitEval(self, js.JSCall(js_fn_name, (_node_js,) + args))


	def js_shutdown_eval(self, expr):
		if isinstance(expr, str)  or  isinstance(expr, unicode):
			expr = js.JSExprSrc(expr)
		elif not isinstance(expr, js.JS):
			raise TypeError, 'Javascript expression must be a string or a JS object'
		return JSShutdownEval(self, expr)

	def js_shutdown_function_call(self, js_fn_name, *args):
		return JSShutdownEval(self, js.JSCall(js_fn_name, (_node_js,) + args))


	def use_css(self, url=None, source=None):
		if url is not None:
			dep = dependencies.CSSURLDependency.dep_for(url)
		elif source is not None:
			dep = dependencies.CSSSourceDependency.dep_for(source)
		else:
			raise TypeError, 'either a URL or source text must be provided'

		return self.depends_on(dep)


	def use_js(self, url=None, source=None):
		if url is not None:
			dep = dependencies.JSURLDependency.dep_for(url)
		elif source is not None:
			dep = dependencies.JSSourceDependency.dep_for(source)
		else:
			raise TypeError, 'either a URL or source text must be provided'

		return self.depends_on(dep)



	def depends_on(self, dependency):
		return AddDependency([dependency], self)



	@staticmethod
	def map_build(pres_ctx, xs):
		return [x.build(pres_ctx)   for x in xs]



	@staticmethod
	def coerce(x):
		if isinstance(x, Pres):
			return x
		else:
			return InnerFragment(x)

	@staticmethod
	def coerce_none_as_none(x):
		if x is None:
			return None
		elif isinstance(x, Pres):
			return x
		else:
			return InnerFragment(x)



	@staticmethod
	def map_coerce(xs):
		return [Pres.coerce(x)   for x in xs]

	@staticmethod
	def map_coerce_none_as_none(xs):
		return [Pres.coerce(x)   for x in xs]







class Resource (Pres, js.JS):
	def __init__(self, rsc_data):
		self.__rsc_data = rsc_data


	def build(self, pres_ctx):
		return HtmlContent([self._url(pres_ctx)])

	def build_js(self, pres_ctx):
		page_rsc = pres_ctx.fragment_view.create_resource(self.__rsc_data, pres_ctx)
		return page_rsc.client_side_js()

	def _url(self, pres_ctx):
		page_rsc = pres_ctx.fragment_view.create_resource(self.__rsc_data, pres_ctx)
		return page_rsc.url



class CompositePres (Pres):
	def build(self, pres_ctx):
		return self.pres(pres_ctx).build(pres_ctx)

	def pres(self, pres_ctx):
		raise NotImplementedError, 'abstract'


class ApplyPerspective (Pres):
	def __init__(self, perspective, child):
		self.__perspective = perspective
		self.__child = Pres.coerce(child)


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
		self._child = Pres.coerce(child)



	def initialise_segment(self, seg, pres_ctx):
		pass

	def build(self, pres_ctx):
		seg = pres_ctx.fragment_view.create_sub_segment(self._child.build(pres_ctx))
		self.initialise_segment(seg, pres_ctx)
		return HtmlContent([seg.reference()])





class EventSource (SubSegmentPres):
	def __init__(self, event_handler, child):
		super(EventSource, self).__init__(child)
		self.__event_handler = event_handler


	def initialise_segment(self, seg, pres_ctx):
		seg.add_event_handler(self.__event_handler)




class JSEval (SubSegmentPres):
	def __init__(self, child, expr):
		super(JSEval, self).__init__(child)
		self._expr = expr


	def initialise_segment(self, seg, pres_ctx):
		raise NotImplementedError, 'abstract'



class JSInitEval (JSEval):
	def initialise_segment(self, seg, pres_ctx):
		expr_src = self._expr.build_js(pres_ctx)
		seg.add_initialise_script(expr_src)



class JSShutdownEval (JSEval):
	def initialise_segment(self, seg, pres_ctx):
		expr_src = self._expr.build_js(pres_ctx)
		seg.add_shutddown_script(expr_src)



class AddDependency (SubSegmentPres):
	def __init__(self, dependencies, child):
		super(AddDependency, self).__init__(child)
		self.__dependencies = dependencies


	def depends_on(self, dependency):
		return AddDependency(self.__dependencies + [dependency], self._child)


	def initialise_segment(self, seg, pres_ctx):
		for dep in self.__dependencies:
			seg.page.add_dependency(dep)




class KeyEventSource (EventSource):
	def __init__(self, keys_and_handlers, child):
		super(KeyEventSource, self).__init__(self.__handle_key_event, child)

		self.__keys_and_handlers = keys_and_handlers

		self.__keydown = [k   for k in keys_and_handlers   if k[0].event_type == KeyAction.KEY_DOWN]
		self.__keyup = [k   for k in keys_and_handlers   if k[0].event_type == KeyAction.KEY_UP]
		self.__keypress = [k   for k in keys_and_handlers   if k[0].event_type == KeyAction.KEY_PRESS]

		self.__keydown_json_str = json.dumps([k[0].__to_json__()   for k in self.__keydown]).replace('"', '\'')
		self.__keyup_json_str = json.dumps([k[0].__to_json__()   for k in self.__keyup]).replace('"', '\'')
		self.__keypress_json_str = json.dumps([k[0].__to_json__()   for k in self.__keypress]).replace('"', '\'')



	def with_key_handler(self, keys, handler):
		keys_and_handlers = [(key, handler)   for key in keys]
		return KeyEventSource(self.__keys_and_handlers + keys_and_handlers, self._child)


	def __handle_key_event(self, event_name, ev_data):
		if event_name == 'keydown':
			ev_key = KeyAction.__from_keydown_json__(ev_data)
			keys_and_handlers = self.__keydown
		elif event_name == 'keyup':
			ev_key = KeyAction.__from_keyup_json__(ev_data)
			keys_and_handlers = self.__keyup
		elif event_name == 'keypress':
			ev_key = KeyAction.__from_keypress_json__(ev_data)
			keys_and_handlers = self.__keypress
		else:
			return False

		for key, handler in keys_and_handlers:
			if ev_key.matches(key):
				return handler(ev_key)

		return False



	def initialise_segment(self, seg, pres_ctx):
		super(KeyEventSource, self).initialise_segment(seg, pres_ctx)
		keydown_json = self.__keydown_json_str
		keyup_json = self.__keyup_json_str
		keypress_json = self.__keypress_json_str
		seg.add_initialise_script('node.onkeydown = function(event) {{return larch.__onkeydown(event, {0});}}'.format(keydown_json))
		seg.add_initialise_script('node.onkeyup = function(event) {{return larch.__onkeyup(event, {0});}}'.format(keyup_json))
		seg.add_initialise_script('node.onkeypress = function(event) {{return larch.__onkeypress(event, {0});}}'.format(keypress_json))




def post_event_js_code(event_name, event_json={}, event_source_js='this'):
	return 'larch.postEvent({0},\'{1}\', {2});'.format(event_source_js, event_name, json.dumps(event_json))

def post_event_js_code_for_handler(event_name, event_json={}, event_source_js='this'):
	return 'javascript:larch.postEvent({0},\'{1}\', {2});'.format(event_source_js, event_name, json.dumps(event_json))

