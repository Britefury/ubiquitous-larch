##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import os
from copy import deepcopy

from britefury.pres.html import Html

from larch.project.project_container import ProjectContainer
from larch.project.subject import RootSubject


class ProjectRoot (ProjectContainer):
	def __init__(self, packageName=None, contents=None):
		super( ProjectRoot, self ).__init__( contents )
		self._pythonPackageName = packageName
		self.__front_page_id = None
		self.__startup_page_id = None

		self.__id_to_page = {}
		self.__page_id_counter = 0

		self._startupExecuted = False


	@property
	def importName(self):
		return self._pythonPackageName   if self._pythonPackageName is not None   else ''


	@property
	def moduleNames(self):
		if self._pythonPackageName is None:
			return []
		else:
			return super( ProjectRoot, self ).moduleNames


	def __getstate__(self):
		state = super( ProjectRoot, self ).__getstate__()
		state['pythonPackageName'] = self._pythonPackageName
		state['frontPageId'] = self.__front_page_id
		state['startupPageId'] = self.__startup_page_id
		return state

	def __setstate__(self, state):
		self.__id_to_page = {}
		self.__page_id_counter = 0
		self._startupExecuted = False

		# Need to initialise the ID table before loading contents
		super( ProjectRoot, self ).__setstate__( state )
		self._pythonPackageName = state['pythonPackageName']
		self.__front_page_id = state.get( 'frontPageId' )
		self.__startup_page_id = state.get( 'startupPageId' )


	def __copy__(self):
		return ProjectRoot( self._pythonPackageName, self[:] )

	def __deepcopy__(self, memo):
		return ProjectRoot( self._pythonPackageName, [ deepcopy( x, memo )   for x in self ] )


	def startup(self):
		if not self._startupExecuted:
			if self._pythonPackageName is not None:
				startupPage = self.startupPage
				if startupPage is not None:
					self._startupExecuted = True
					__import__( startupPage.importName )

	def reset(self):
		self._startupExecuted = False



	def export(self, path):
		myPath = path

		if self._pythonPackageName is not None:
			components = self._pythonPackageName.split( '.' )
			for c in components:
				myPath = os.path.join( myPath, c )
				if not os.path.exists( myPath ):
					os.mkdir( myPath )
					initPath = os.path.join( myPath, '__init__.py' )
					f = open( initPath, 'w' )
					f.write( '' )
					f.close()

		self.exportContents( myPath )


	def _register_root(self, root, takePriority):
		# No need to register the root package; this is the root package
		pass

	def _unregister_root(self, root):
		# No need to unregister the root package; this is the root package
		pass




	@property
	def pythonPackageName(self):
		self._incr.on_access()
		return self._pythonPackageName

	@pythonPackageName.setter
	def pythonPackageName(self, name):
		oldName = self._pythonPackageName
		self._pythonPackageName = name
		self._incr.on_changed()
		if self.__change_history__ is not None:
			def _apply():
				self.pythonPackageName = name
			def _revert():
				self.pythonPackageName = oldName
			self.__change_history__.addChange(_apply, _revert, 'Project root set python package name' )



	def _register_page(self, page, takePriority):
		pageId = page._id

		if pageId is not None  and  pageId in self.__id_to_page  and  takePriority:
			# page ID already in use
			# Take it, and make a new one for the page that is currently using it

			# Get the other page that is currently using the page ID
			otherPage = self.__id_to_page[pageId]

			# Make new page ID
			self.__page_id_counter = max( self.__page_id_counter, len( self.__id_to_page) )
			otherPageId = self.__page_id_counter
			self.__page_id_counter += 1

			# Re-assign
			self.__id_to_page[pageId] = page
			page._id = pageId
			self.__id_to_page[otherPageId] = otherPage
			otherPage._id = otherPageId
		elif pageId is None  or  ( pageId in self.__id_to_page  and  not takePriority ):
			# Either, no page ID or page ID already in use and not taking priority
			# Create a new one
			self.__page_id_counter = max( self.__page_id_counter, len( self.__id_to_page) )
			pageId = self.__page_id_counter
			self.__page_id_counter += 1
			page._id = pageId

		self.__id_to_page[pageId] = page

	def _unregister_page(self, node):
		nodeId = node._id
		del self.__id_to_page[nodeId]


	def get_page_by_id(self, nodeId):
		return self.__id_to_page.get( nodeId )



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



	def _present_header(self, fragment):
		return Html('<span class="project_index_text">Project contents</span>')






	def __subject__(self, enclosing_subject, location_trail, perspective):
		return RootSubject(enclosing_subject, location_trail, self, perspective)
