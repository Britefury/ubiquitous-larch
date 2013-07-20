##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.pres import post_event_js_code_for_handler
from britefury.pres.html import Html
from britefury.live.abstract_live import AbstractLive
from britefury.live.live_value import LiveValue
from britefury.live.live_function import LiveFunction
from britefury.pres.controls import button

def dropdown_expander(header, content, state=None, on_expand=None):
	"""
	Create a drop-down expander control. Consists of a button that the user clicks to open the control, display the content below

	:param header: the contents of the header button
	:param content: the content that is displayed when open
	:param state: the state; either in the form of a boolean which will be the initial state - True for open, False for closed - or a live value that contains the state
	:param on_expand: a callback invoked when the expander is expanded or contracted; of the form function(state)
	:return: the expander control
	"""
	def expand_fn(x):
		state.value = x

	if state is None:
		state = LiveValue(False)
	elif isinstance(state, bool):
		state = LiveValue(state)
	elif isinstance(state, LiveValue):
		pass
	elif isinstance(state, AbstractLive):
		expand_fn = None
	else:
		raise TypeError, 'state must be None, a bool or an AbstractLive, not an {0}'.format(type(state).__name__)


	def on_clicked(event_name, ev_data):
		s = state.static_value
		new_state = not s
		if expand_fn is not None:
			expand_fn(new_state)
		if on_expand is not None:
			on_expand(new_state)





	@LiveFunction
	def result():
		s = state.value
		if s is True:
			hdr = Html('<button onclick="{0}" style="width: 100%; text-align: left">'.format(post_event_js_code_for_handler('clicked')), header, '</button>')
			hdr = hdr.js_function_call('larch.controls.initButton', {'icons': {'primary': 'ui-icon-minus'}})
			hdr = hdr.with_event_handler('clicked', on_clicked)
			ct = Html('<div class="dropdown_expander_content">', content, '</div>')
			return Html(hdr, ct)
		elif s is False:
			hdr = Html('<button onclick="{0}" style="width: 100%; text-align: left">'.format(post_event_js_code_for_handler('clicked')), header, '</button>')
			hdr = hdr.js_function_call('larch.controls.initButton', {'icons': {'primary': 'ui-icon-plus'}})
			hdr = hdr.with_event_handler('clicked', on_clicked)
			return hdr
		else:
			raise TypeError, 'drop down expander: state type unknown'

	return result




