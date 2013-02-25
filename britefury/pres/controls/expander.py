##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.pres import post_event_js_code_for_handler
from britefury.pres.html import Html
from britefury.live.abstract_live import AbstractLive
from britefury.live.live_value import LiveValue
from britefury.live.live_function import LiveFunction

def dropdown_expander(header, content, state=None, on_expand=None):
	def expand_fn(x):
		state.value = x

	if state is None:
		state = LiveValue(False)
	elif isinstance(state, bool):
		state = LiveValue(state)
	elif isinstance(state, AbstractLive):
		expand_fn = on_expand
	else:
		raise TypeError, 'state must be None, a bool or an AbstractLive, not an {0}'.format(type(state).__name__)


	def on_clicked(event_name, ev_data):
		s = state.static_value
		expand_fn(not s)





	@LiveFunction
	def result():
		s = state.value
		if s is True:
			hdr = Html('<div class="dropdown_expander_header" onclick="{0}">-'.format(post_event_js_code_for_handler('clicked')), header, '</div>').with_event_handler('clicked', on_clicked)
			ct = Html('<div class="dropdown_expander_content">', content, '</div>')
			return Html(hdr, ct)
		elif s is False:
			hdr = Html('<div class="dropdown_expander_header" onclick="{0}">+'.format(post_event_js_code_for_handler('clicked')), header, '</div>').with_event_handler('clicked', on_clicked)
			return hdr
		else:
			raise TypeError, 'drop down expander: state type unknown'

	return result


