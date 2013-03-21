##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def code_mirror(text, immediate_events=False, config=None, on_edit=None, on_focus=None, on_blur=None):
	if config is None:
		config = {}
	textarea = Html('<textarea>{text}</textarea>'.format(text=text))
	textarea = textarea.js_function_call('larch.controls.initCodeMirror', config, immediate_events)
	p = Html('<div>', textarea, '</div>')
	p = p.use_css('codemirror/lib/codemirror.css')
	p = p.use_js('codemirror/lib/codemirror.js')
	p = p.use_js('bridge_codemirror.js')
	if on_edit is not None:
		p = p.with_event_handler('code_mirror_edit', lambda event_name, ev_data: on_edit(ev_data))
	if on_focus is not None:
		p = p.with_event_handler('code_mirror_focus', lambda event_name, ev_data: on_focus())
	if on_blur is not None:
		p = p.with_event_handler('code_mirror_blur', lambda event_name, ev_data: on_blur())
	return p
  