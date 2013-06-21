##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.live.live_value import LiveValue
from britefury.live.live_function import LiveFunction
from britefury.live.tracked_live_list import TrackedLiveList

from britefury.pres.html import Html
from britefury.pres.controls import menu, text_entry, button

from larch.project.project_node import ProjectNode
from larch.worksheet.worksheet import Worksheet
from larch import project



class GUIBox (object):
	def __init__(self, create_gui):
		self.__create_gui = create_gui


	def close(self):
		self.__create_gui.value = Html('<span></span>')


class NewNodeGUI (GUIBox):
	def __init__(self, create_gui, container, node_type_name, initial_name, node_create_fn):
		super(NewNodeGUI, self).__init__(create_gui)
		self.__name = initial_name
		self.__container = container
		self.__node_type_name = node_type_name
		self.__node_create_fn = node_create_fn


	def __present__(self, fragment):
		def on_edit(text):
			self.__name = text

		def on_create():
			self.__container.append(self.__node_create_fn(self.__name))
			self.close()

		def on_cancel():
			self.close()

		return Html('<div class="gui_box">',
				'<span class="gui_section_1">Create {0}</span><br>'.format(self.__node_type_name),
				'<table>',
				'<tr><td><span class="gui_label">Name:</span></td><td>', text_entry.text_entry(self.__name, on_edit=on_edit), '</td></tr>',
				'<tr><td>', button.button('Cancel', on_cancel), '</td><td>', button.button('Create', on_create), '</td></tr>',
				'</table>',
				'</div>')






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


	def _present_header(self, fragment):
		raise NotImplementedError, 'abstract'


	def __resolve__(self, name, subject):
		contents_map = self.contents_map
		node = contents_map.get(name)
		if node is not None:
			subject.add_step(focus=node)
			return node
		else:
			return None



	def __present__(self, fragment):
		create_gui = LiveValue(Html('<span></span>'))

		header = self._present_header(fragment)


		def on_new_package():
			create_gui.value = NewNodeGUI(create_gui, self, 'package', 'Package', lambda name: project.project_package.ProjectPackage(name))

		def on_new_worksheet():
			create_gui.value = NewNodeGUI(create_gui, self, 'worksheet', 'Worksheet', lambda name: project.project_page.ProjectPage(name, Worksheet()))


		new_package_item = menu.item('New package', on_new_package)
		new_worksheet_item = menu.item('New worksheet', on_new_worksheet)
		create_page_item = menu.sub_menu('-', [new_package_item, new_worksheet_item])

		container_menu = menu.menu([create_page_item], drop_down=True)



		contents = [
			'<div class="project_package">',
			'<div class-"project_container_header">',
			'<table><tr><td>',
			container_menu,
			'</td><td>',
			header,
			'</td></tr></table>',
			'</div>',
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
