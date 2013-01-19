from britefury.element.event_elem import post_event_js_code_for_handler
from britefury.pres.html import Html


def button(button_text, action_fn):
	def handle_event(event_name, ev_data):
		action_fn()

	return Html('<button onclick="{0}">{1}</button>'.format(post_event_js_code_for_handler('clicked'), button_text)).with_event_handler('clicked', handle_event)
