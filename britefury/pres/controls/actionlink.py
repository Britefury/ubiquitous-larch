from britefury.pres.html import Html


def action_link(link_text, action_fn):
	def handle_event(event_name, ev_data):
		action_fn()

	return Html('<a href="javascript:" onclick="javascript:__larch.postEvent($(this),\'clicked\', {});">' + link_text + '</a>').with_event_handler('clicked', handle_event)
  