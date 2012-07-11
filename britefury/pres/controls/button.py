from britefury.pres.html import Html


def button(button_text, action_fn):
	def handle_event(event_name, ev_data):
		action_fn()

	return Html('<button onclick="javascript:__larch.postEvent($(this),\'clicked\', {});">' + button_text + '</button>').with_event_handler('clicked', handle_event)
