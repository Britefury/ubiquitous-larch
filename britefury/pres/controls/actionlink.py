from britefury.element.event_elem import post_event_js_code_for_handler
from britefury.pres.html import Html


def action_link(link_text, action_fn):
	def handle_event(event_name, ev_data):
		action_fn()

	return Html('<a href="javascript:" onclick="{0}">{1}</a>'.format(post_event_js_code_for_handler('clicked'), link_text)).with_event_handler('clicked', handle_event)
  