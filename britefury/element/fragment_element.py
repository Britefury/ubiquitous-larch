##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.element.element import Element






class FragmentElement (Element):
	_unique_id_counter = 1


	def __init__(self, fragment_view, content):
		super(FragmentElement, self).__init__()
		self.__fragment_view = fragment_view
		self.__content = content
		if self.__content is not None:
			self.__content.parent = self

		self.__unique_id = FragmentElement._unique_id_counter
		FragmentElement._unique_id_counter += 1


	@property
	def fragment_id(self):
		return 'lch_frag_' + str(self.__unique_id)



	@property
	def content(self):
		return self.__content

	@content.setter
	def content(self, c):
		if self.__content is not None:
			self.__content.parent = None
		self.__content = c
		c.parent = self
		if self._root_element is not None:
			self._root_element._notify_fragment_modified(self)


	@property
	def children(self):
		yield self.__content


	def __html__(self, level):
		return self._container(level, {'class': '__lch_fragment_elem', 'id': self.fragment_id}, self.__content.__html__(level))


	def _content_html(self, level):
		return self.__content.__html__(level)
