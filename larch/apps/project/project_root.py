##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import os
import sys
from copy import deepcopy

from larch.pres.html import Html
from larch.controls import text_entry, button

from larch.apps.project.project_container import ProjectContainer


class ProjectRoot (ProjectContainer):
	def __init__(self, package_name=None, contents=None):
		super( ProjectRoot, self ).__init__( contents )
		self.__python_package_name = package_name
		self.__front_page_id = None
		self.__startup_page_id = None

		self.__id_to_page = {}
		self.__page_id_counter = 0

		self.__startup_executed = False


	@property
	def import_name(self):
		return self.__python_package_name   if self.__python_package_name is not None   else ''


	@property
	def module_names(self):
		if self.__python_package_name is None:
			return []
		else:
			return super( ProjectRoot, self ).module_names


	def __getstate__(self):
		state = super( ProjectRoot, self ).__getstate__()
		state['python_package_name'] = self.__python_package_name
		state['front_page_id'] = self.__front_page_id
		state['startup_page_id'] = self.__startup_page_id
		return state

	def __setstate__(self, state):
		self.__id_to_page = {}
		self.__page_id_counter = 0
		self.__startup_executed = False

		# Need to initialise the ID table before loading contents
		super( ProjectRoot, self ).__setstate__( state )
		self.__python_package_name = state.get('python_package_name')
		self.__front_page_id = state.get( 'front_page_id' )
		self.__startup_page_id = state.get( 'startup_page_id' )


	def __copy__(self):
		return ProjectRoot( self.__python_package_name, self[:] )

	def __deepcopy__(self, memo):
		return ProjectRoot( self.__python_package_name, [ deepcopy( x, memo )   for x in self ] )


	def startup(self):
		if not self.__startup_executed:
			if self.__python_package_name is not None:
				startupPage = self.startupPage
				if startupPage is not None:
					self.__startup_executed = True
					__import__( startupPage.import_name )

	def reset(self):
		self.__startup_executed = False



	def export(self, path):
		my_path = path

		if self.__python_package_name is not None:
			components = self.__python_package_name.split( '.' )
			for c in components:
				my_path = os.path.join( my_path, c )
				if not os.path.exists( my_path ):
					os.mkdir( my_path )
					init_path = os.path.join( my_path, '__init__.py' )
					f = open( init_path, 'w' )
					f.write( '' )
					f.close()

		self.export_contents( my_path )


	def _register_root(self, root, takePriority):
		# No need to register the root package; this is the root package
		pass

	def _unregister_root(self, root):
		# No need to unregister the root package; this is the root package
		pass




	@property
	def python_package_name(self):
		self._incr.on_access()
		return self.__python_package_name

	@python_package_name.setter
	def python_package_name(self, name):
		self.__set_python_package_name_no_incr_change(name)
		self._incr.on_changed()

	def __set_python_package_name_no_incr_change(self, name):
		old_name = self.__python_package_name
		self.__python_package_name = name
		if self.__change_history__ is not None:
			def _apply():
				self.python_package_name = name
			def _revert():
				self.python_package_name = old_name
			self.__change_history__.addChange(_apply, _revert, 'Project root set python package name' )



	def _register_page(self, page, takePriority):
		page_id = page._id

		if page_id is not None  and  page_id in self.__id_to_page  and  takePriority:
			# page ID already in use
			# Take it, and make a new one for the page that is currently using it

			# Get the other page that is currently using the page ID
			other_page = self.__id_to_page[page_id]

			# Make new page ID
			self.__page_id_counter = max( self.__page_id_counter, len( self.__id_to_page) )
			other_page_id = self.__page_id_counter
			self.__page_id_counter += 1

			# Re-assign
			self.__id_to_page[page_id] = page
			page._id = page_id
			self.__id_to_page[other_page_id] = other_page
			other_page._id = other_page_id
		elif page_id is None  or  ( page_id in self.__id_to_page  and  not takePriority ):
			# Either, no page ID or page ID already in use and not taking priority
			# Create a new one
			self.__page_id_counter = max( self.__page_id_counter, len( self.__id_to_page) )
			page_id = self.__page_id_counter
			self.__page_id_counter += 1
			page._id = page_id

		self.__id_to_page[page_id] = page

	def _unregister_page(self, node):
		node_id = node._id
		del self.__id_to_page[node_id]


	def get_page_by_id(self, node_id):
		return self.__id_to_page.get( node_id )



	@property
	def root_node(self):
		return self


	@property
	def frontPage(self):
		self._incr.on_access()
		self.startup()
		return self.__id_to_page.get( self.__front_page_id )   if self.__front_page_id is not None   else None

	@frontPage.setter
	def frontPage(self, page):
		self.__front_page_id = page._id   if page is not None   else None
		self._incr.on_changed()



	@property
	def startupPage(self):
		self._incr.on_access()
		return self.__id_to_page.get( self.__startup_page_id )   if self.__startup_page_id is not None   else None

	@startupPage.setter
	def startupPage(self, page):
		self.__startup_page_id = page._id   if page is not None   else None
		self._incr.on_changed()



	def __import_resolve__(self, name, fullname, path):
		if self.python_package_name is None  or  self.python_package_name == '':
			return super(ProjectRoot, self).__import_resolve__(name, fullname, path)
		else:
			return _RootNameFinder(self.python_package_name, self).__import_resolve__(name, fullname, path)



	def _present_header_contents(self, fragment):
		return Html('<span class="project_index_text">Project contents</span>')



	def __present__(self, fragment):
		super_pres = super(ProjectRoot, self).__present__(fragment)

		def _on_set_package_name(name):
			self.__set_python_package_name_no_incr_change(name)

		def _on_unload(event):
			subject = fragment.subject
			try:
				unload_modules_and_display_notification = subject.document.unload_modules_and_display_notification
			except AttributeError:
				print 'WARNING: Could not unload_all_imported_modules; method unavailable'
				raise
			else:
				unload_modules_and_display_notification(fragment)


		python_package_name = self.python_package_name
		python_package_name = python_package_name   if python_package_name is not None  else ''
		entry = text_entry.text_entry(python_package_name, on_edit=_on_set_package_name)

		unload_button = button.button('Unload', _on_unload)

		contents = [
			'<div class="larch_app_title_bar"><h1 class="page_title">Project</h1></div>',
			'<p class="project_root_package_name">Root package name: ', entry, '<br><span class="notes_text">(this is the base name from which the contents of this project will be importable)</span></p>',
			'<p class="project_reset">Unload modules imported from project (Esc - U): ', unload_button, '</p>',
			super_pres,
		]
		return Html(*contents).use_css(url="/static/larch/project.css")



class _RootNameFinder (object):
	def __init__(self, root_name, model):
		if '.' in root_name:
			self.__head, _, tail = root_name.partition('.')
			self.__next = _RootNameFinder(tail, model)
			self.__model = None
		else:
			self.__head = root_name
			self.__next = None
			self.__model = model


	def __import_resolve__(self, name, fullname, path):
		if name == self.__head:
			if self.__next is not None:
				return self.__next
			else:
				return super(ProjectRoot, self.__model)
		else:
			return None


	def __load_module__(self, document, fullname):
		try:
			return sys.modules[fullname]
		except KeyError:
			pass

		# Empty module
		return document.new_module(fullname, self)



