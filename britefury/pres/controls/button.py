##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.pres import post_event_js_code_for_handler
from britefury.pres.html import Html


def button(button_text, action_fn):
	p = Html('<button onclick="{0}">{1}</button>'.format(post_event_js_code_for_handler('clicked'), button_text)).js_function_call('larch.controls.initButton')
	p = p.with_event_handler('clicked', lambda event_name, ev_data: action_fn())
	return p