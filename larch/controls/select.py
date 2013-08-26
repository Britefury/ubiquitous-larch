##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html


def select(option_value_content_pairs, value, on_choose=None):
	def _on_choose(event):
		if on_choose is not None:
			on_choose(event, event.data)

	options = [Html('<option value="{0}"{1}>'.format(opt_value, (' selected'   if opt_value == value   else '')), content, '</option>')   for opt_value, content in option_value_content_pairs]

	p = Html(*(['<select>'] + options + ['</select>'])).js_function_call('larch.controls.initSelect')
	p = p.with_event_handler('select_choose', _on_choose)
	p = p.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
	return p
