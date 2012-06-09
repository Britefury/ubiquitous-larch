##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.element.element import Element


class AbstractEventElement (Element):
	_unique_id_counter = 1


	def __init__(self, content):
		super(AbstractEventElement, self).__init__()
		self._content = content
		if self._content is not None:
			self._content.parent = self

		self.__unique_id = AbstractEventElement._unique_id_counter
		AbstractEventElement._unique_id_counter += 1


	@property
	def event_id(self):
		return 'lch_event_' + str(self.__unique_id)


	def handle_event(self, event_name, ev_data):
		raise NotImplementedError, 'abstract'



	@property
	def content(self):
		return self._content


	@property
	def children(self):
		yield self._content


	def _set_root_element(self, root):
		if self._root_element is not None:
			self._root_element._unregister_event_element(self.event_id)
		super(AbstractEventElement, self)._set_root_element(root)
		if self._root_element is not None:
			self._root_element._register_event_element(self.event_id, self)


	def __html__(self):
		raise NotImplementedError, 'abstract'


	def _content_html(self):
		return Element.html(self._content)