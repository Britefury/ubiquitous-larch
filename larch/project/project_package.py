import os
from copy import deepcopy

from britefury.pres.html import Html
from britefury.pres.controls import menu

from larch.project.project_node import RenameNodeGUI
from larch.project.project_container import ProjectContainer



class ProjectPackage (ProjectContainer):
	def __init__(self, name='', contents=None):
		super( ProjectPackage, self ).__init__( contents )
		self._name = name


	@property
	def import_name(self):
		return self.parent.import_name + '.' + self._name


	def __getstate__(self):
		state = super( ProjectPackage, self ).__getstate__()
		state['name'] = self._name
		return state

	def __setstate__(self, state):
		super( ProjectPackage, self ).__setstate__( state )
		self._name = state['name']

	def __copy__(self):
		return ProjectPackage( self._name, self[:] )

	def __deepcopy__(self, memo):
		return ProjectPackage( self._name, [ deepcopy( x, memo )   for x in self ] )


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
			self.__change_history__.addChange( _apply, _revert, 'Package set name' )



	def export(self, path):
		my_path = os.path.join( path, self.name )
		if not os.path.exists( my_path ):
			os.mkdir( my_path )

		# Create an empty init module if none is present
		if '__init__' not in self.contents_map:
			init_path = os.path.join( my_path, '__init__.py' )
			f = open( init_path, 'w' )
			f.write( '' )
			f.close()

		self.export_contents( my_path )



	def _present_menu_items(self, fragment, gui):
		super_items = super(ProjectPackage, self)._present_menu_items(fragment, gui)

		def on_rename():
			gui.value = RenameNodeGUI(gui, self)

		rename_item = menu.item('Rename', on_rename)

		return [rename_item] + super_items


	def _present_header_contents(self, fragment):
		return Html('<span class="project_package_text">{0}</span>'.format(self.name))

