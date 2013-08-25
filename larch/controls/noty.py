##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres import js, pres, popup
from larch.pres.html import Html


_js_createNotyPopup = js.JSName('larch.controls.createNotyPopup')


class noty (object):
	def __init__(self, contents, **options):
		self.__contents = pres.Pres.coerce(contents).use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
		self.__options = options


	def show_on(self, target):
		p = popup.Popup(self.__contents, target)
		p.show_using_js_function_call(_js_createNotyPopup, self.__options)
