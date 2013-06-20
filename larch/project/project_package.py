import os
from copy import deepcopy

from britefury.pres.html import Html

from larch.project.project_container import ProjectContainer







class ProjectPackage (ProjectContainer):
	def __init__(self, name='', contents=None):
		super( ProjectPackage, self ).__init__( contents )
		self._name = name


	@property
	def importName(self):
		return self.parent.importName + '.' + self._name


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


	def getName(self):
		self._incr.on_access()
		return self._name

	def setName(self, name):
		oldName = self._name
		self._name = name
		self._incr.on_changed()
		if self.__change_history__ is not None:
			self.__change_history__.addChange( lambda: self.setName( name ), lambda: self.setName( oldName ), 'Package set name' )



	def export(self, path):
		myPath = os.path.join( path, self.name )
		if not os.path.exists( myPath ):
			os.mkdir( myPath )

		# Create an empty init module if none is present
		if '__init__' not in self.contentsMap:
			initPath = os.path.join( myPath, '__init__.py' )
			f = open( initPath, 'w' )
			f.write( '' )
			f.close()

		self.exportContents( myPath )



	name = property( getName, setName )



	def _present_header(self, fragment):
		return Html('<span class="project_package_text">{0}</span>'.format(self.name))


