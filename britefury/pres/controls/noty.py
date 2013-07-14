##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def noty(text, **options):
	options['text'] = text
	# An empty span element
	return Html('<span></span>').js_eval('noty({text: "Hello world"});')