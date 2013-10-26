##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.event_handler import EventHandler
from larch.pres.html import Html
from larch.pres.pres import CompositePres


class focusable (CompositePres):
	def __init__(self, contents, on_gain_focus=None, on_lose_focus=None):
		"""
		Make an element focusable
		:param contents: contents that are to be made focusable
		:param on_gain_focus: [optional] a function of the form function(event) that is invoked when the element gains focus
		:param on_lose_focus: [optional] a function of the form function(event) that is invoked when the element loses focus
		:return: the control
		"""
		self.__contents = contents
		self.gain_focus = EventHandler()
		self.lose_focus = EventHandler()
		if on_gain_focus is not None:
			self.gain_focus.connect(on_gain_focus)
		if on_lose_focus is not None:
			self.lose_focus.connect(on_lose_focus)


	def pres(self, pres_ctx):
		p = Html(self.__contents).js_function_call('larch.controls.initFocusable').js_shutdown_function_call('larch.controls.shutdownFocusable')
		p = p.with_event_handler('gain_focus', self.gain_focus)
		p = p.with_event_handler('lose_focus', self.lose_focus)
		p = p.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
		return p
