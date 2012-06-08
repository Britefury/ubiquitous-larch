##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.element.element import Element




class HtmlContentElem (Element):
	def __init__(self, contents):
		self.__contents = contents



	@property
	def children(self):
		for c in self.__contents:
			if isinstance(c, Element):
				yield c


	def __html__(self):
		return ''.join([Element.html(x)  for x in self.__contents])
