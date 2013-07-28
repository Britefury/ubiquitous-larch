##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def separator():
	"""
	Create a separator menu item
	:return: the separator
	"""
	p = Html('<li></li>')
	return p


def item(item_content, on_select=None):
	"""
	Create a menu item control. Must be placed within a menu control, created with :menu:.

	:param item_content: the HTML content of the menu item
	:param on_select: a callback invoked when the menu item is activated by the user
	:return: the menu item control
	"""
	p = Html('<li><a href="#">', item_content, '</a></li>')
	if on_select is not None:
		p = p.with_event_handler('menu_select', lambda event_name, ev_data: on_select())
	return p


def sub_menu(item_content, items):
	"""
	Create a sub-menu item control. Must be placed within a menu control, created with :menu:.

	:param item_content: the HTML content of the menu item
	:param items: the items to be displayed within the submenu
	:return: the menu item control
	"""
	sub = ['<ul class="popup_box">'] + list(items) + ['</ul>']
	return Html(*['<li class="popup_box"><a href="#">', item_content, '</a>'] + sub + ['</li>'])


def menu(items, drop_down=False):
	"""
	Create a JQuery UI menu control.

	:param items: the items to be displayed within the menu
	:param drop_down: if True, the menu appears below the control that activates it
	:return: the menu control
	"""
	options = {}
	if drop_down:
		options['position'] = {'my': 'left top', 'at': 'left bottom'}
	return Html(*['<ul class="popup_box">'] + list(items) + ['</ul>']).js_function_call('larch.controls.initMenu', options).use_js('/static/bridge_jqueryui.js')
