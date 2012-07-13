##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.element.element import Element
from britefury.element.elem_with_id import ElementWithId




class JSElement (ElementWithId):
	def __init__(self, js_fn_names, content):
		super(JSElement, self).__init__()
		self.__js_fn_names = js_fn_names
		self._content = content
		if self._content is not None:
			self._content.parent = self



	@property
	def content(self):
		return self._content


	@property
	def children(self):
		yield self._content




	def _set_root_element(self, root):
		super(JSElement, self)._set_root_element(root)
		if self._root_element is not None:
			js_lines = ['{0}(document.getElementById("{1}").childNodes[0]);'.format(fn_name, self.element_id)   for fn_name in self.__js_fn_names]
			self._root_element._queue_js_to_execute('\n'.join(js_lines))



	def __html__(self):
		content_html = Element.html(self._content)
		return '<span class="__lch_exec_js_elem" id="{0}">{1}</span>'.format(self.element_id, content_html)
