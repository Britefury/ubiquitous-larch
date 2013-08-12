##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres import js
from larch.pres.html import Html


js_noty = js.JSName('noty')

def noty(text, **options):
	options['text'] = text
	# An empty span element
	return Html('<span></span>').js_eval(js_noty({'text': text}))