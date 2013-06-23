##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor

from britefury.live.live_value import LiveValue

from britefury.pres.html import Html
from britefury.pres.controls import menu, text_entry, button



class _GUIBox (object):
	def __init__(self, gui):
		self.__gui = gui


	def close(self):
		self.__gui.value = Html('<span></span>')



class RenameNodeGUI (_GUIBox):
	def __init__(self, gui, node):
		super(RenameNodeGUI, self).__init__(gui)
		self.__node = node
		self.__name = node.name


	def __present__(self, fragment):
		def on_edit(text):
			self.__name = text

		def on_rename():
			self.__node.name = self.__name
			self.close()

		def on_cancel():
			self.close()

		return Html('<div class="gui_box">',
				'<span class="gui_section_1">Rename</span><br>',
				'<table>',
				'<tr><td><span class="gui_label">Name:</span></td><td>', text_entry.text_entry(self.__name, on_edit=on_edit), '</td></tr>',
				'<tr><td>', button.button('Cancel', on_cancel), '</td><td>', button.button('Rename', on_rename), '</td></tr>',
				'</table>',
				'</div>')




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



	def _present_menu_items(self, fragment, gui):
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



