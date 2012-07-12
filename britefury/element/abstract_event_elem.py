##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.element.elem_with_id import ElementWithId


class AbstractEventElement (ElementWithId):
	def __init__(self, content):
		super(AbstractEventElement, self).__init__()
		self._content = content
		if self._content is not None:
			self._content.parent = self


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
			self._root_element._unregister_event_element(self.element_id)
		super(AbstractEventElement, self)._set_root_element(root)
		if self._root_element is not None:
			self._root_element._register_event_element(self.element_id, self)


	def __html__(self):
		raise NotImplementedError, 'abstract'


	def _content_html(self):
		return Element.html(self._content)