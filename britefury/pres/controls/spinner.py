##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def spinner(action_fn, name='spinner', initial_value=0):
	def on_slide(event_name, ev_data):
		action_fn(ev_data)

	spin = Html('<input name={0} value={1} />'.format(name, initial_value))
	spin = spin.js_function_call('larch.controls.initSpinner')
	spin = spin.with_event_handler("spinner_change", on_slide)
	spin = spin.use_js('/bridge_jqueryui.js')
	return spin
