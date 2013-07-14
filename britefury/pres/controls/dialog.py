##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def dialog(contents, options=None):
	if options is None:
		options = {}
	return Html('<div>', contents, '</div>').js_function_call('larch.controls.initDialog', options).use_js('/static/bridge_jqueryui.js')
