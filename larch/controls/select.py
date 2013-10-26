##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.event_handler import EventHandler
from larch.pres.html import Html
from larch.pres.pres import CompositePres


class select (CompositePres):
	def __init__(self, option_value_content_pairs, value, on_choose=None):
		self.__options = [Html('<option value="{0}"{1}>'.format(opt_value, (' selected'   if opt_value == value   else '')), content, '</option>')   for opt_value, content in option_value_content_pairs]
		self.choose = EventHandler()

	def pres(self, pres_ctx):
		p = Html(*(['<select>'] + self.__options + ['</select>'])).js_function_call('larch.controls.initSelect')
		p = p.with_event_handler('select_choose', lambda event: self.choose(event, event.data))
		p = p.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
		return p
