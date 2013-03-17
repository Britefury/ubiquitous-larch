##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.pres import post_event_js_code_for_handler
from britefury.pres.html import Html


def slider(action_fn):
	def on_slide(event_name, ev_data):
		action_fn(ev_data)

	div = Html('<div></div>')
	div = div.js_function_call('larch.controls.initSlider')
	div = div.with_event_handler("slider_change", on_slide)
	div = div.use_js('bridge_jqueryui.js')
	return div
