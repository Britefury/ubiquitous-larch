##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import sys

from larch.apps import project


class PageFinder (object):
	def __init__(self, moduleLoader):
		self._moduleLoader = moduleLoader


	def import_resolve(self, name, fullname, path):
		return None


	def load_module(self, fullname):
		return self._moduleLoader.load_module( fullname )





class PackageFinder (object):
	def __init__(self, project_subject, model):
		self._project_subject = project_subject
		if model is None:
			model = self._project_subject._model
		self._model = model


	def import_resolve(self, name, fullname, path):
		item = self._model.contents_map.get( name )

		if item is not None:
			model = item

			if isinstance( model, project.project_page.ProjectPage ):
				# We have found a page: get its subject
				page_subject = self._project_subject._pageSubject( model )
				# Now, check if it has a 'createModuleLoader' method - if it has, then we can use it. Otherwise, we can't
				try:
					createModuleLoader = page_subject.createModuleLoader
				except AttributeError:
					return None
				else:
					# The subject has a 'createModuleLoader' attribute - invoke it to create the module loader, for the module import system to use
					return PageFinder( createModuleLoader( self._project_subject.document ) )
			elif isinstance( model, project.project_package.ProjectPackage ):
				return PackageFinder( self._project_subject, model )
			else:
				raise TypeError, 'unrecognised model type'
		else:
			return None



	# Package module loading
	def load_module(self, fullname):
		try:
			return sys.modules[fullname]
		except KeyError:
			pass

		# First, see if there is an '__init__; page
		init_page = self._model.contents_map.get( '__init__' )

		if init_page is not None and isinstance( init_page, project.project_page.ProjectPage ):
			# We have found a page called '__init__' - get its subject
			page_subject = self._project_subject._pageSubject( init_page )
			# Now, check if it has a 'createModuleLoader' method - if it has, then we can use it. Otherwise, use the default
			try:
				createModuleLoader = page_subject.createModuleLoader
			except AttributeError:
				return self._default_load_module( fullname )
			else:
				loader = createModuleLoader( self._project_subject.document )
				return loader.load_module( fullname )

		return self._default_load_module( fullname )


	def _default_load_module(self, fullname):
		return self._project_subject.document.new_module( fullname, self )




class RootFinder (object):
	def __init__(self, project_subject, python_package_name, package_finder):
		self._project_subject = project_subject
		self._package_finder = package_finder
		if python_package_name is not None:
			self._name, _, self._name_suffix = python_package_name.partition( '.' )
		else:
			self._name = self._name_suffix = None


	def import_resolve(self, name, fullname, path):
		if name == self._name:
			if self._name_suffix == '':
				return self._package_finder
			else:
				return RootFinder( self._project_subject, self._name_suffix, self._package_finder )
		else:
			return None

	def load_module(self, fullname):
		try:
			return sys.modules[fullname]
		except KeyError:
			pass

		return self._project_subject.document.new_module( fullname, self )
