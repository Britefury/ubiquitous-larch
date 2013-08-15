##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html
from larch.pres.pres import CompositePres
from larch.pres.resource import PresLink, PresIFrame


_all_extensions = ['menu', 'goto', 'status', 'navigation', 'scale']


_deck_js = """
function init_deck_js(node) {
	var container = $(node);
	var slides = container.find('.slide');
	$.deck(slides);
}
"""


def _deck_libs(p, extensions, style, transition):
	if extensions is None:
		extensions = _all_extensions

	p = p.use_css('/static/deckjs/core/deck.core.css')

	for ext in extensions:
		p = p.use_css('/static/deckjs/extensions/{0}/deck.{0}.css'.format(ext))

	if style is not None:
		p = p.use_css('/static/deckjs/themes/style/{0}.css'.format(style))
	if transition is not None:
		p = p.use_css('/static/deckjs/themes/transition/{0}.css'.format(transition))

	p = p.use_js('/static/deckjs/modernizr.custom.js')

	p = p.use_js('/static/deckjs/core/deck.core.js')

	for ext in extensions:
		p = p.use_js('/static/deckjs/extensions/{0}/deck.{0}.js'.format(ext))

	return p


def Slide(contents):
	return Html('<section class="slide">', contents, '</section>')


class Deck (object):
	def __init__(self, extensions=None, style=None, transition='horizontal-slide'):
		self.__extensions = extensions
		self.__style = style
		self.__transition = transition
		self.__slides = []


	def append(self, *slides):
		self.__slides.extend(slides)
		return self


	def extend(self, slides):
		self.__slides.extend(slides)
		return self


	def link(self, link_content):
		p = Html('<div class="deck-container">').extend(self.__slides).append('</div>')
		p = p.js_function_call('init_deck_js').use_js(source=_deck_js)
		p = _deck_libs(p, self.__extensions, self.__style, self.__transition)
		p = PresLink(p, link_content)
		return p


	def iframe(self, width=None, height=None):
		p = Html('<div class="deck-container">').extend(self.__slides).append('</div>')
		p = p.js_function_call('init_deck_js').use_js(source=_deck_js)
		p = _deck_libs(p, self.__extensions, self.__style, self.__transition)
		p = PresIFrame(p, width, height)
		return p
