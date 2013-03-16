##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def code_mirror(text, on_edit=None, config=None):
	if config is None:
		config = {}
	textarea = Html('<textarea>{text}</textarea>'.format(text=text)).js_function_call('__larchControls.initCodeMirror', config)
	p = Html('<div>', textarea, '</div>')
	if on_edit is not None:
		p = p.with_event_handler('code_mirror_edit', lambda event_name, ev_data: on_edit(ev_data))
	return p
  