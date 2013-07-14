##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def select(option_value_content_pairs, value, on_choose=None):
	options = [Html('<option value="{0}"{1}>'.format(opt_value, (' selected'   if opt_value == value   else '')), content, '</option>')   for opt_value, content in option_value_content_pairs]

	p = Html(*(['<select>'] + options + ['</select>'])).js_function_call('larch.controls.initSelect')
	if on_choose is not None:
		p = p.with_event_handler('select_choose', lambda event_name, ev_data: on_choose(ev_data))
	p = p.use_js('/static/bridge_jqueryui.js')
	return p
