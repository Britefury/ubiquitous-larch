##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
##-*************************
from larch.incremental import IncrementalValueMonitor
from larch.live import LiveValue

from larch.pres.html import Html
from larch.controls import menu


class Tool (object):
	def __init__(self, tool_container):
		self.__tool_container = tool_container


	def close(self):
		self.__tool_container.value = Html('<span></span>')


class ProjectNode (object):
	def __init__(self):
		self._incr = IncrementalValueMonitor()
		self.__change_history__ = None
		self._parent = None


	def is_page(self):
		return False


	@property
	def import_name(self):
		raise NotImplementedError, 'abstract'


	@property
	def module_names(self):
		raise NotImplementedError, 'abstract'


	def __getstate__(self):
		return {}

	def __setstate__(self, state):
		self._incr = IncrementalValueMonitor()
		self.__change_history__ = None
		self._parent = None


	def export(self, path):
		raise NotImplementedError, 'abstract'




	def __trackable_contents__(self):
		return None


	def _set_parent(self, parent, takePriority):
		self._parent = parent
		new_root = parent.root_node
		if new_root is not None:
			self._register_root( new_root, takePriority )


	def _clear_parent(self):
		old_root = self.root_node
		if old_root is not None:
			self._unregister_root( old_root )
		self._parent = None


	def _register_root(self, root, takePriority):
		pass

	def _unregister_root(self, root):
		pass


	@property
	def path_to_root(self):
		path = []
		node = self
		while node is not None:
			path.append(node)
			node = node._parent
		return path


	@property
	def parent(self):
		return self._parent


	@property
	def root_node(self):
		return self._parent.root_node   if self._parent is not None   else None



	def _present_menu_items(self, fragment, tool_container):
		raise NotImplementedError, 'abstract'

	def _present_menu(self, fragment, gui):
		menu_items = self._present_menu_items(fragment, gui)
		create_page_item = menu.sub_menu('-', menu_items)
		return menu.menu([create_page_item], drop_down=True)

	def _present_header_contents(self, fragment):
		raise NotImplementedError, 'abstract'

	def _present_header(self, fragment):
		gui = LiveValue(Html('<span></span>'))
		header = self._present_header_contents(fragment)

		contents = [
			'<div>',
			'<table><tr><td>',
			self._present_menu(fragment, gui),
			'</td><td>',
			header,
			'</td></tr></table>',
			'</div>',
			'<div class="project_gui_container">',
			gui,
			'</div>'
		]

		return Html(*contents)


