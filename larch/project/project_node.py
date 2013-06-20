##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor


class ProjectNode (object):
	def __init__(self):
		self._incr = IncrementalValueMonitor()
		self.__change_history__ = None
		self._parent = None


	@property
	def importName(self):
		raise NotImplementedError, 'abstract'


	@property
	def moduleNames(self):
		raise NotImplementedError, 'abstract'


	def __getstate__(self):
		return {}

	def __setstate__(self, state):
		self._incr = IncrementalValueMonitor()
		self.__change_history__ = None
		self._parent = None


	def export(self, path):
		raise NotImplementedError, 'abstract'




	def __trackable_contents__(self):
		return None


	def _set_parent(self, parent, takePriority):
		self._parent = parent
		newRoot = parent.root_node
		if newRoot is not None:
			self._register_root( newRoot, takePriority )


	def _clear_parent(self):
		oldRoot = self.root_node
		if oldRoot is not None:
			self._unregister_root( oldRoot )
		self._parent = None


	def _register_root(self, root, takePriority):
		pass

	def _unregister_root(self, root):
		pass


	@property
	def path_to_root(self):
		path = []
		node = self
		while node is not None:
			path.append(node)
			node = node._parent
		return path


	@property
	def parent(self):
		return self._parent


	@property
	def root_node(self):
		return self._parent.root_node   if self._parent is not None   else None




