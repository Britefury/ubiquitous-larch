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


	def _setParent(self, parent, takePriority):
		self._parent = parent
		newRoot = parent.rootNode
		if newRoot is not None:
			self._registerRoot( newRoot, takePriority )


	def _clearParent(self):
		oldRoot = self.rootNode
		if oldRoot is not None:
			self._unregisterRoot( oldRoot )
		self._parent = None


	def _registerRoot(self, root, takePriority):
		pass

	def _unregisterRoot(self, root):
		pass


	@property
	def parent(self):
		return self._parent


	@property
	def rootNode(self):
		return self._parent.rootNode   if self._parent is not None   else None




