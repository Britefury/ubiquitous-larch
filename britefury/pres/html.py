##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.pres import Pres
from britefury.webdoc.web_document import HtmlContent


class Html (Pres):
	def __init__(self, *contents):
		self.__contents = []
		for c in contents:
			if isinstance(c, str) or isinstance(c, unicode):
				self.__contents.append(c)
			else:
				self.__contents.append(Pres.coerce(c))


	def build(self, pres_ctx):
		cs = []
		for c in self.__contents:
			if isinstance(c, str) or isinstance(c, unicode):
				cs.append(c)
			else:
				cs.append(c.build(pres_ctx))
		return HtmlContent(cs)