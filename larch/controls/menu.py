##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.event_handler import EventHandler
from larch.pres.html import Html
from larch.pres.pres import CompositePres


def separator():
	"""
	Create a separator menu item
	:return: the separator
	"""
	p = Html('<li></li>')
	return p


class item (CompositePres):
	def __init__(self, item_content, on_select=None):
		"""
		Create a menu item control. Must be placed within a menu control, created with :menu:.

		:param item_content: the HTML content of the menu item
		:param on_select: a callback invoked when the menu item is activated by the user
		:return: the menu item control
		"""
		self.__item_content = item_content
		self.select = EventHandler()
		if on_select is not None:
			self.select.connect(on_select)

	def pres(self, pres_ctx):
		p = Html('<li><a>', self.__item_content, '</a></li>')
		p = p.with_event_handler('menu_select', self.select)
		return p


def sub_menu(item_content, items):
	"""
	Create a sub-menu item control. Must be placed within a menu control, created with :menu:.

	:param item_content: the HTML content of the menu item
	:param items: the items to be displayed within the submenu
	:return: the menu item control
	"""
	sub = ['<ul class="popup_box">'] + list(items) + ['</ul>']
	return Html(*['<li class="popup_box"><a>', item_content, '</a>'] + sub + ['</li>'])


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
	return Html(*['<ul class="popup_box">'] + list(items) + ['</ul>']).js_function_call('larch.controls.initMenu', options).use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
