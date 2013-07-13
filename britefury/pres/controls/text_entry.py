##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def text_entry(value, on_edit=None):
	p = Html('<input type="text" value="{0}"></input>'.format(value)).js_function_call('larch.controls.initTextEntry')
	if on_edit is not None:
		p = p.with_event_handler('text_entry_edit', lambda event_name, ev_data: on_edit(ev_data))
	p = p.use_js('/static/bridge_jqueryui.js')
	return p
