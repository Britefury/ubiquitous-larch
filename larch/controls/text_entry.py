##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html


def text_entry(value, on_edit=None, size=None, width=None):
	sz = ''
	if size is not None:
		sz += ' size="{0}"'.format(size)
	if width is not None:
		sz += ' style="width: {0};"'.format(width)
	p = Html('<input type="text" value="{0}"{1}></input>'.format(value, sz)).js_function_call('larch.controls.initTextEntry')
	if on_edit is not None:
		p = p.with_event_handler('text_entry_edit', lambda event_name, ev_data: on_edit(ev_data))
	p = p.use_js('/static/larch_ui.js').use_css('/static/larch_ui.css')
	return p
