##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html


def focusable(contents, on_gain_focus=None, on_lose_focus=None):
	"""
	Make an element focusable
	:param contents: contents that are to be made focusable
	:param on_gain_focus: [optional] a function of the form function(event) that is invoked when the element gains focus
	:param on_lose_focus: [optional] a function of the form function(event) that is invoked when the element loses focus
	:return: the control
	"""
	def gain(event):
		if on_gain_focus is not None:
			on_gain_focus(event)

	def lose(event):
		if on_lose_focus is not None:
			on_lose_focus(event)

	p = Html(contents).js_function_call('larch.controls.initFocusable').js_shutdown_function_call('larch.controls.shutdownFocusable')
	p = p.with_event_handler('gain_focus', gain)
	p = p.with_event_handler('lose_focus', lose)
	p = p.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
	return p
