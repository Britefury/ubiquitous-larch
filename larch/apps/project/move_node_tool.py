##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
##-*************************
from larch.pres.html import Html

from larch.controls import button, action_link
from larch.apps.project.project_node import Tool
from larch.apps.project.project_container import ProjectContainer




class MoveNodeTool (Tool):
	def __init__(self, tool_container, node):
		super(MoveNodeTool, self).__init__(tool_container)
		self.__node = node
		self.__root = node.root_node


	def __present__(self, fragment):
		def on_move(destination):
			self.__node.parent.remove(self.__node)
			destination.append(self.__node)
			self.close()

		def on_cancel(event):
			self.close()

		return Html('<div class="tool_box">',
				'<span class="gui_section_1">Move to:</span><br>',
				'<ul class="project_move_dest_list">',
				self.__container_dest(self.__root, on_move),
				'</ul>',
				button.button('Cancel', on_cancel),
				'</div>')


	def __container_item(self, container, on_choose):
		if container is self.__root:
			return action_link.action_link('Project Index', lambda event: on_choose(container), css_class='project_move_to_root')
		else:
			return action_link.action_link(container.name, lambda event: on_choose(container), css_class='project_move_to_package')

	def __container_dest(self, container, on_choose):
		item = self.__container_item(container, on_choose)
		children = [child   for child in container   if child is not self.__node  and  isinstance(child, ProjectContainer)]
		child_dests = [self.__container_dest(child, on_choose)   for child in children]
		return Html(*([item, '<ul class="project_move_dest_list">'] + child_dests + ['</ul>']))
