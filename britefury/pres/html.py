##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import cgi

from britefury.pres.pres import Pres
from britefury.dynamicsegments.segment import HtmlContent


class Html (Pres):
	def __init__(self, *contents):
		self.__contents = []
		for c in contents:
			if isinstance(c, str) or isinstance(c, unicode):
				self.__contents.append(c)
			else:
				self.__contents.append(Pres.coerce(c))


	def append(self, *contents):
		return self.extend(contents)

	def extend(self, contents):
		for c in contents:
			if isinstance(c, str) or isinstance(c, unicode):
				self.__contents.append(c)
			else:
				self.__contents.append(Pres.coerce(c))
		return self


	def build(self, pres_ctx):
		cs = []
		for c in self.__contents:
			if isinstance(c, str) or isinstance(c, unicode):
				cs.append(c)
			else:
				cs.append(c.build(pres_ctx))
		return HtmlContent(cs)


	@staticmethod
	def div(x, cls=None):
		if cls is None:
			return Html('<div>', x, '</div>')
		else:
			return Html('<div class={0}>'.format(cls), x, '</div>')



	@staticmethod
	def escape_str(x):
		return cgi.escape(x)



