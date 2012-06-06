##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
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
		self.__content = c
		c.parent = self
		if self._root_element is not None:
			self._root_element._notify_fragment_modified(self)


	@property
	def children(self):
		yield self.__content


	def __html__(self):
		content_html = Element.html(self.__content)
		return '<span id="{0}">{1}</span>'.format(self.fragment_id, content_html)


	def _content_html(self):
		return Element.html(self.__content)