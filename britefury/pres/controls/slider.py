##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def slider(release_fn, slide_fn=None, width=None, options=None):
	def on_change(event_name, ev_data):
		release_fn(ev_data)

	def on_slide(event_name, ev_data):
		slide_fn(ev_data)

	if options is None:
		options = {}

	if width is None:
		div = Html('<div></div>')
	else:
		div = Html('<div style="width: {0};"></div>'.format(width))
	div = div.js_function_call('larch.controls.initSlider', slide_fn is not None, options)
	div = div.with_event_handler("slider_change", on_change)
	if slide_fn is not None:
		div = div.with_event_handler("slider_slide", on_slide)
	div = div.use_js('/static/bridge_jqueryui.js')
	return div



def live_slider(live, update_on_slide=False, width=None, options=None):
	if options is None:
		options = {}

	options['value'] = live.value

	def on_slide(value):
		live.value = value

	slide_fn = on_slide   if update_on_slide   else None
	return slider(on_slide, slide_fn, width, options)
