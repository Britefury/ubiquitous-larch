##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.pres import post_event_js_code_for_handler
from britefury.pres.html import Html


def action_link(link_text, action_fn):
	p = Html('<a href="javascript:" onclick="{0}">{1}</a>'.format(post_event_js_code_for_handler('clicked'), link_text)).with_event_handler('clicked', handle_event)
	p = p.with_event_handler('clicked', lambda event_name, ev_data: action_fn())
	return p
  