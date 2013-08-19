##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import sys
from larch.apps import project
from larch.live import LiveValue, LiveFunction

from larch.live import TrackedLiveList

from larch.pres.html import Html
from larch.controls import menu

from larch.apps.project.project_node import ProjectNode
from larch.apps.project.new_node_tool import NewNodeTool
from larch.apps import project
from larch.apps.worksheet.worksheet import Worksheet




class ProjectContainer (ProjectNode):
	def __init__(self, contents=None):
		super( ProjectContainer, self ).__init__()
		self._contents = TrackedLiveList()
		self._contents.change_listener = self.__contents_changed
		self._contents_map_live = LiveFunction( self._compute_contents_map )
		if contents is not None:
			self[:] = contents


	@property
	def module_names(self):
		names = []
		for c in self._contents:
			names.extend( c.module_names )
		return names


	def __getstate__(self):
		state = super( ProjectContainer, self ).__getstate__()
		state['contents'] = self._contents[:]
		return state

	def __setstate__(self, state):
		super( ProjectContainer, self ).__setstate__( state )
		self._contents = TrackedLiveList(state.get('contents'))
		self._contents.change_listener = self.__contents_changed
		self._contents_map_live = LiveFunction( self._compute_contents_map )

		for x in self._contents:
			x._set_parent( self, True )


	def _compute_contents_map(self):
		m = {}
		self._incr.on_access()
		for x in self._contents:
			m[x.name] = x
		return m


	def __len__(self):
		self._incr.on_access()
		return len( self._contents )

	def __getitem__(self, index):
		self._incr.on_access()
		return self._contents[index]

	def __iter__(self):
		for x in self._contents:
			self._incr.on_access()
			yield x

	def __contains__(self, x):
		self._incr.on_access()
		return x in self._contents

	def index_of_by_id(self, x):
		for i, y in enumerate( self._contents ):
			if x is y:
				return i
		return -1



	def __setitem__(self, index, x):
		self._contents[index] = x

	def __delitem__(self, index):
		del self._contents[index]

	def append(self, x):
		self._contents.append( x )

	def insert(self, i, x):
		self._contents.insert( i, x )

	def remove(self, x):
		self._contents.remove( x )




	@property
	def contents_map(self):
		return self._contents_map_live.value


	def export_contents(self, myPath):
		for x in self._contents:
			x.export( myPath )



	def __trackable_contents__(self):
		return self._contents.__trackable_contents__()



	def _register_root(self, root, takePriority):
		super( ProjectContainer, self )._register_root( root, takePriority )
		for x in self._contents:
			x._register_root( root, takePriority )

	def _unregister_root(self, root):
		super( ProjectContainer, self )._unregister_root( root )
		for x in self._contents:
			x._unregister_root( root )




	def __contents_changed(self, old_contents, new_contents):
		prev = set(old_contents)
		cur = set(new_contents)
		added = cur - prev
		removed = prev - cur
		for x in removed:
			x._clear_parent()
		for x in added:
			x._set_parent( self, False )
		self._incr.on_changed()


	def __resolve__(self, name, subject):
		contents_map = self.contents_map
		node = contents_map.get(name)
		if node is not None:
			subject.add_step(focus=node)
			return node
		else:
			return None



	def __import_resolve__(self, name, fullname, path):
		return self.contents_map.get(name)


	def __load_module__(self, document, fullname):
		try:
			return sys.modules[fullname]
		except KeyError:
			pass

		# First, see if there is an '__init__; page
		init_page = self.contents_map.get('__init__')

		if init_page is not None and init_page.is_page():
			# We have found a page called '__init__'
			# Now, check if it has a '__load_module__' method - if it has, then we can use it. Otherwise, create a blank module
			try:
				loader = init_page.content.__load_module__
			except AttributeError:
				pass
			else:
				module = loader(document, fullname)
				if module is not None:
					return module

		return document.new_module(fullname, self)



	def _present_menu_items(self, fragment, tool_container):
		def on_new_package():
			tool_container.value = NewNodeTool(tool_container, self, 'package', 'Package', lambda name: project.project_package.ProjectPackage(name))

		def on_new_worksheet():
			tool_container.value = NewNodeTool(tool_container, self, 'worksheet', 'Worksheet', lambda name: project.project_page.ProjectPage(name, Worksheet()))


		new_package_item = menu.item('New package', on_new_package)
		new_worksheet_item = menu.item('New worksheet', on_new_worksheet)

		return [new_package_item, new_worksheet_item]


	def __present__(self, fragment):
		create_gui = LiveValue(Html('<span></span>'))

		header = self._present_header(fragment)

		contents = [
			'<div class="project_package">',
			header,
			create_gui,
			'<div class="project_container_contents">',
		]

		xs = self._contents[:]
		xs.sort(key=lambda x: (not isinstance(x, ProjectContainer), x.name))

		for x in xs:
			contents.extend(['<div>', x, '</div>'])

		contents.extend([
			'</div>',
			'</div>'
		])
		return Html(*contents)
