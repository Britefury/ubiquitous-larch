##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.pres import post_event_js_code_for_handler
from britefury.pres.html import Html


def focusable(contents, on_gain_focus=None, on_lose_focus=None):
	"""
	Make an element focusable
	:param contents: contents that are to be made focusable
	:param on_gain_focus: [optional] a function of the form function() that is invoked when the element gains focus
	:param on_lose_focus: [optional] a function of the form function() that is invoked when the element loses focus
	:return: the control
	"""
	p = Html(contents).js_function_call('larch.controls.makeFocusable')
	if on_gain_focus is not None:
		p = p.with_event_handler('gain_focus', lambda event_name, ev_data: on_gain_focus())
	if on_lose_focus is not None:
		p = p.with_event_handler('lose_focus', lambda event_name, ev_data: on_lose_focus())
	return p
