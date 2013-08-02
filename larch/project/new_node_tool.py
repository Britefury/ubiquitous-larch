##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html
from britefury.pres.controls import text_entry, button, action_link

from larch import project
from larch.project.project_node import Tool


class NewNodeTool (Tool):
	def __init__(self, tool_container, container, node_type_name, initial_name, node_create_fn):
		super(NewNodeTool, self).__init__(tool_container)
		self.__name = initial_name
		self.__container = container
		self.__node_type_name = node_type_name
		self.__node_create_fn = node_create_fn


	def __present__(self, fragment):
		def on_edit(text):
			self.__name = text

		def on_create():
			self.__container.append(self.__node_create_fn(self.__name))
			self.close()

		def on_cancel():
			self.close()

		return Html('<div class="gui_box">',
				'<span class="gui_section_1">Create {0}</span><br>'.format(self.__node_type_name),
				'<table>',
				'<tr><td><span class="gui_label">Name:</span></td><td>', text_entry.text_entry(self.__name, on_edit=on_edit), '</td></tr>',
				'<tr><td>', button.button('Cancel', on_cancel), '</td><td>', button.button('Create', on_create), '</td></tr>',
				'</table>',
				'</div>')
