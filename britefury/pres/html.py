##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************

from britefury.pres.pres import Pres
from britefury.element.html_content import HtmlContent


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