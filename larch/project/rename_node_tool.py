##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html
from larch.controls import text_entry

from larch.controls import button
from larch.project.project_node import Tool



class RenameNodeTool (Tool):
	def __init__(self, tool_container, node):
		super(RenameNodeTool, self).__init__(tool_container)
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

		return Html('<div class="tool_box">',
				'<span class="gui_section_1">Rename</span><br>',
				'<table>',
				'<tr><td><span class="gui_label">Name:</span></td><td>', text_entry.text_entry(self.__name, on_edit=on_edit), '</td></tr>',
				'<tr><td>', button.button('Cancel', on_cancel), '</td><td>', button.button('Rename', on_rename), '</td></tr>',
				'</table>',
				'</div>')


