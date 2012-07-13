##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.element.element import Element




class HtmlContentElem (Element):
	def __init__(self, contents):
		super(HtmlContentElem, self).__init__()
		self.__contents = contents
		for c in contents:
			if isinstance(c, Element):
				c.parent = self



	@property
	def children(self):
		for c in self.__contents:
			if isinstance(c, Element):
				yield c


	def __html__(self):
		return ''.join([Element.html(x)  for x in self.__contents])
