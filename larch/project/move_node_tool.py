##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html
from britefury.pres.controls import text_entry, button, action_link

from larch import project
from larch.project.project_node import Tool
from larch.project.project_container import ProjectContainer




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

		def on_cancel():
			self.close()

		return Html('<div class="gui_box">',
				'<span class="gui_section_1">Move to:</span><br>',
				'<ul class="project_move_dest_list">',
				self.__container_dest(self.__root, on_move),
				'</ul>',
				button.button('Cancel', on_cancel),
				'</div>')


	def __container_item(self, container, on_choose):
		if container is self.__root:
			return action_link.action_link('Project Index', lambda: on_choose(container), css_class='project_move_to_root')
		else:
			return action_link.action_link(container.name, lambda: on_choose(container), css_class='project_move_to_package')

	def __container_dest(self, container, on_choose):
		item = self.__container_item(container, on_choose)
		children = [child   for child in container   if child is not self.__node  and  isinstance(child, ProjectContainer)]
		child_dests = [self.__container_dest(child, on_choose)   for child in children]
		return Html(*([item, '<ul class="project_move_dest_list">'] + child_dests + ['</ul>']))
