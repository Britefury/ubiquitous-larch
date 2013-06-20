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
	def import_name(self):
		raise NotImplementedError, 'abstract'


	@property
	def module_names(self):
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
		new_root = parent.root_node
		if new_root is not None:
			self._register_root( new_root, takePriority )


	def _clear_parent(self):
		old_root = self.root_node
		if old_root is not None:
			self._unregister_root( old_root )
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




