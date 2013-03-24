##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def ckeditor(text, immediate_events=False, config=None, on_edit=None, on_focus=None, on_blur=None):
	if text == '':
		text = '<p></p>'
	if config is None:
		config = {}
	p = Html('<div contenteditable="true">{text}</div>'.format(text=text)).js_function_call('larch.controls.initCKEditor', config, immediate_events)
	p = p.use_js('/ckeditor/ckeditor.js')
	p = p.use_js('/bridge_ckeditor.js')
	if on_edit is not None:
		p = p.with_event_handler('ckeditor_edit', lambda event_name, ev_data: on_edit(ev_data))
	if on_focus is not None:
		p = p.with_event_handler('ckeditor_focus', lambda event_name, ev_data: on_focus())
	if on_blur is not None:
		p = p.with_event_handler('ckeditor_blur', lambda event_name, ev_data: on_blur())
	return p
