##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.live.live_function import LiveFunction
from britefury.live.tracked_live_list import TrackedLiveList

from britefury.pres.html import Html

from larch.project.project_node import ProjectNode


class ProjectContainer (ProjectNode):
	def __init__(self, contents=None):
		super( ProjectContainer, self ).__init__()
		self._contents = TrackedLiveList()
		self._contentsMapLive = LiveFunction( self._computeContentsMap )
		if contents is not None:
			self[:] = contents
		self._contents.change_listener = self.__contents_changed


	@property
	def moduleNames(self):
		names = []
		for c in self._contents:
			names.extend( c.moduleNames )
		return names


	def __getstate__(self):
		state = super( ProjectContainer, self ).__getstate__()
		state['contents'] = self._contents
		return state

	def __setstate__(self, state):
		super( ProjectContainer, self ).__setstate__( state )
		self._contents = state['contents']
		self._contentsMapLive = LiveFunction( self._computeContentsMap )

		for x in self._contents:
			x._setParent( self, True )


	def _computeContentsMap(self):
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

	def indexOfById(self, x):
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
	def contentsMap(self):
		return self._contentsMapLive.value


	def exportContents(self, myPath):
		for x in self._contents:
			x.export( myPath )



	def __trackable_contents__(self):
		return self._contents.__trackable_contents__()



	def _registerRoot(self, root, takePriority):
		super( ProjectContainer, self )._registerRoot( root, takePriority )
		for x in self._contents:
			x._registerRoot( root, takePriority )

	def _unregisterRoot(self, root):
		super( ProjectContainer, self )._unregisterRoot( root )
		for x in self._contents:
			x._unregisterRoot( root )




	def __contents_changed(self, old_contents, new_contents):
		prev = set(old_contents)
		cur = set(new_contents)
		added = cur - prev
		removed = prev - cur
		for x in removed:
			x._clearParent()
		for x in added:
			x._setParent( self, False )
		self._incr.on_changed()



	def __present_container_contents__(self, fragment):
		contents = [
			'<div class="project_container_contents">',
		]

		for x in self._contents:
			contents.extend(['<div>', x, '</div>'])

		contents.append('</div>')
		return Html(*contents)


