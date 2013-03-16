##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def item(item_content, on_select):
	return Html('<li><a href="#">', item_content, '</a></li>').with_event_handler('menu_select', lambda event_name, ev_data: on_select())

def sub_menu(item_content, *items):
	sub = ['<ul>'] + list(items) + ['</ul>']
	return Html(*['<li><a href="#">', item_content, '</a>'] + sub + ['</li>'])

def menu(*items):
	return Html(*['<ul>'] + list(items) + ['</ul>']).js_function_call('__larchControls.initMenu')
