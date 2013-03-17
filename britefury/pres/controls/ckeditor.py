##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def ckeditor(text, on_edit=None, immediate_events=False, config=None):
	if text == '':
		text = '<p></p>'
	if config is None:
		config = {}
	p = Html('<div contenteditable="true">{text}</div>'.format(text=text)).js_function_call('larchControls.initCKEditor', config, immediate_events)
	if on_edit is not None:
		p = p.with_event_handler('ckeditor_edit', lambda event_name, ev_data: on_edit(ev_data))
	return p
