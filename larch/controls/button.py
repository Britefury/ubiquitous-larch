##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.pres import post_event_js_code_for_handler
from larch.pres.html import Html


def button(text=None, action_fn=None, primary_icon=None, secondary_icon=None, disabled=False):
	"""
	Create a JQuery UI button
	:param text: the button content (can include HTML)
	:param action_fn: a callback that is invoked when the button is pressed
	:param primary_icon: primary icon (see JQuery UI icon classes)
	:param secondary_icon: secondary icon (see JQuery UI icon classes)
	:param disabled: disable the button
	:return: the button control
	"""
	def on_click(event):
		if action_fn is not None:
			action_fn()

	options = {}
	if disabled is not False:
		options['disabled'] = True

	if primary_icon is not None  or  secondary_icon is not None:
		icons = {}
		if primary_icon is not None:
			icons['primary'] = primary_icon
		if secondary_icon is not None:
			icons['secondary'] = secondary_icon
		options['icons'] = icons

	if text is not None:
		p = Html('<button onclick="{0}">'.format(post_event_js_code_for_handler('clicked')), text, '</button>').js_function_call('larch.controls.initButton', options)
	else:
		options['text'] = False
		p = Html('<button onclick="{0}"></button>').js_function_call('larch.controls.initButton', options)
	p = p.with_event_handler('clicked', on_click).use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
	return p