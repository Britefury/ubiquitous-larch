##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def code_mirror(text, config, on_edit):
	textarea = Html('<textarea>{text}</textarea>'.format(text=text)).js_function_call('__larchControls.initCodeMirror', config)
	event_catcher = Html('<div>', textarea, '</div>').with_event_handler('code_mirror_edit', lambda event_name, ev_data: on_edit(ev_data))
	return event_catcher
  