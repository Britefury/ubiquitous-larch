##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def item(item_content, on_select=None):
	p = Html('<li><a href="#">', item_content, '</a></li>')
	if on_select is not None:
		p = p.with_event_handler('menu_select', lambda event_name, ev_data: on_select())
	return p

def sub_menu(item_content, items):
	sub = ['<ul class="popup_box">'] + list(items) + ['</ul>']
	return Html(*['<li class="popup_box"><a href="#">', item_content, '</a>'] + sub + ['</li>'])

def menu(items, drop_down=False):
	options = {}
	if drop_down:
		options['position'] = {'my': 'left top', 'at': 'left bottom'}
	return Html(*['<ul class="popup_box">'] + list(items) + ['</ul>']).js_function_call('larch.controls.initMenu', options).use_js('/bridge_jqueryui.js')
