##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
##-*************************
import os
from copy import deepcopy

from larch.controls import menu

from larch.pres.html import Html

from larch.apps.project.project_node import ProjectNode
from larch.apps.project.rename_node_tool import RenameNodeTool
from larch.apps.project.move_node_tool import MoveNodeTool



class ProjectPage (ProjectNode):
	def __init__(self, name='', data=None):
		super( ProjectPage, self ).__init__()
		self._id = None
		self._name = name
		self._data = data


	def is_page(self):
		return True


	@property
	def import_name(self):
		if self._name == '__init__':
			return self.parent.import_name
		else:
			return self.parent.import_name + '.' + self._name


	@property
	def module_names(self):
		return [ self.import_name ]



	def __getstate__(self):
		state = super( ProjectPage, self ).__getstate__()
		state['name'] = self._name
		state['data'] = self._data
		state['id'] = self._id
		return state

	def __setstate__(self, state):
		super( ProjectPage, self ).__setstate__( state )
		self._name = state['name']
		self._data = state['data']
		self._id = state.get( 'id' )

	def __copy__(self):
		return ProjectPage( self._name, self._data )

	def __deepcopy__(self, memo):
		return ProjectPage( self._name, deepcopy( self._data, memo ) )


	@property
	def name(self):
		self._incr.on_access()
		return self._name

	@name.setter
	def name(self, name):
		old_name = self._name
		self._name = name
		self._incr.on_changed()
		if self.__change_history__ is not None:
			def _apply():
				self.name = name
			def _revert():
				self.name = old_name
			self.__change_history__.addChange(_apply, _revert, 'Page set name' )


	@property
	def data(self):
		self._incr.on_access()
		return self._data


	def export(self, path):
		filename = self.name + '.py'
		my_path = os.path.join( path, filename )
		s = self.data.exportAsString( self.name )
		f = open( my_path, 'w' )
		f.write( s )
		f.close()




	def _register_root(self, root, takePriority):
		root._register_page( self, takePriority )

	def _unregister_root(self, root):
		root._unregister_page( self )



	def __trackable_contents__(self):
		return [ self.data ]


	@property
	def node_id(self):
		return self._id


	def __resolve_self__(self, subject):
		subject.add_step(focus=self._data, title=self.name)
		return self._data


	def __import_resolve_self__(self, fullname, path):
		return self._data


	# No need for __load_module__, since __import_resolve_self__ bounces on to the content


	def _present_menu_items(self, fragment, tool_container):
		def on_rename(event):
			tool_container.value = RenameNodeTool(tool_container, self)

		def on_move(event):
			tool_container.value = MoveNodeTool(tool_container, self)

		def on_delete(event):
			self._parent.remove(self)

		rename_item = menu.item('Rename', on_rename)
		move_item = menu.item('Move', on_move)
		delete_item = menu.item('Delete', on_delete)

		return [rename_item, menu.separator(), move_item, menu.separator(), delete_item]


	def _present_header_contents(self, fragment):
		project_location = fragment.subject.location
		path_to_root = self.path_to_root
		trail = list(reversed([node.name   for node in path_to_root[:-1]]))
		page_location = '/'.join([project_location] + trail)

		return Html('<a class="project_page_text" href="{0}">{1}</a>'.format(page_location, self.name))


	def __present__(self, fragment):
		return self._present_header(fragment)


