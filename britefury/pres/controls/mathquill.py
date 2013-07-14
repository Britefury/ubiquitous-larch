##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def mathquill(latex, editable=True, immediate_events=False, on_edit=None):
	p = Html(u'<span>{latex}</span>'.format(latex=latex)).js_function_call('larch.controls.initMathquill', editable, immediate_events)
	p = p.use_css('/static/mathquill-0.9.2/mathquill.css')
	p = p.use_js('/static/mathquill-0.9.2/mathquill.min.js')
	p = p.use_js('/static/bridge_mathquill.js')
	if on_edit is not None:
		p = p.with_event_handler('mathquill_edit', lambda event_name, ev_data: on_edit(ev_data))
	return p
