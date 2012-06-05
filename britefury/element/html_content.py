##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************
from britefury.element.element import Element




class HtmlContent (Element):
	def __init__(self, contents):
		self.__contents = contents



	@property
	def children(self):
		for c in self.__contents:
			if isinstance(c, Element):
				yield c


	def __html__(self):
		return ''.join([Element.html(x)  for x in self.__contents])
