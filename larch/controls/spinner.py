##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html


def spinner(action_fn, name='spinner', initial_value=0):
	def on_slide(event_name, ev_data):
		action_fn(ev_data)

	spin = Html('<input name={0} value={1} />'.format(name, initial_value))
	spin = spin.js_function_call('larch.controls.initSpinner')
	spin = spin.with_event_handler("spinner_change", on_slide)
	spin = spin.use_js('/static/larch_ui.js').use_css('/static/larch_ui.css')
	return spin




def live_spinner(live, name='spinner'):
	def on_change(value):
		live.value = value

	return spinner(on_change, name, live.static_value)
