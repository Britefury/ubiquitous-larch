##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
class Element (object):
	def __init__(self):
		self._parent = None
		self._root_element = None


	@property
	def parent(self):
		return self._parent

	@parent.setter
	def parent(self, p):
		self._parent = p
		if p is not None  and  p.root_element is not None:
			self._set_root_element(p.root_element)


	@property
	def children(self):
		return iter([])


	@property
	def root_element(self):
		return self._root_element


	def _set_root_element(self, root):
		self._root_element = root
		for c in self.children:
			c._set_root_element(root)



	def is_ancestor_of(self, x):
		while x is not None:
			if x is self:
				return True
			x = x.parent
		return False


	def ancestor_of_elements(self, xs):
		elements = set()
		for x in xs:
			if self.is_ancestor_of(x):
				elements.add(x)
		return elements


	def is_descendant_of(self, ancestor):
		x = self
		while x is not None:
			if x is ancestor:
				return True
			x = x.parent
		return False


	def descendant_of_one_of(self, ancestors):
		x = self
		while x is not None:
			if x in ancestors:
				return x
			x = x.parent
		return None



	def __html__(self):
		return ''


	@staticmethod
	def html(x):
		if isinstance(x, str) or isinstance(x, unicode):
			return x
		else:
			return x.__html__()
