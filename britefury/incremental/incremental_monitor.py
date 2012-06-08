##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import weakref
import unittest
import gc




class IncrementalMonitor (object):
	UNINITIALISED = 'UNINITIALISED'
	REFRESH_REQUIRED = 'REFRESH_REQUIRED'
	REFRESH_NOT_REQUIRED = 'REFRESH_NOT_REQUIRED'


	_current_computation = None


	def __init__(self, owner=None):
		self._owner = owner
		self._incremental_state = IncrementalMonitor.UNINITIALISED
		self._outgoing_dependencies = None
		self._listeners = None



	owner = property(lambda self: self._owner)
	has_listeners = property(lambda self: (self._listeners is not None  and  len(self._listeners) > 0))
	outgoing_dependences = property(lambda self: (set(self._outgoing_dependencies.keys())   if self._outgoing_dependencies is not None   else set()))
	has_outgoing_dependences = property(lambda self: (self._outgoing_dependencies is not None  and  len(self._outgoing_dependencies) > 0))



	def add_listener(self, listener):
		if self._listeners is None:
			self._listeners = []
		if listener in self._listeners:
			return
		self._listeners.append(listener)

	def remove_listener(self, listener):
		if self._listeners is not None:
			try:
				self._listeners.remove(listener)
			except ValueError:
				pass



	def _on_value_access(self):
		if IncrementalMonitor._current_computation is not None:
			IncrementalMonitor._current_computation._on_incoming_dependency_access(self)

	def _notify_changed(self):
		if self._incremental_state != IncrementalMonitor.REFRESH_REQUIRED:
			self._incremental_state = IncrementalMonitor.REFRESH_REQUIRED
			self._emit_changed()

			if self._outgoing_dependencies is not None:
				for dep in self._outgoing_dependencies.keys():
					dep._notify_changed()

	def _notify_refreshed(self):
		self._incremental_state = IncrementalMonitor.REFRESH_NOT_REQUIRED


	def _emit_changed(self):
		if self._listeners is not None:
			for listener in self._listeners:
				listener(self)


	@staticmethod
	def _push_current_computation(computation):
		f = IncrementalMonitor._current_computation
		IncrementalMonitor._current_computation = computation
		return f

	@staticmethod
	def _pop_current_computation(prev_computation):
		IncrementalMonitor._current_computation = prev_computation



	@staticmethod
	def block_access_tracking():
		return IncrementalMonitor._push_current_computation(None)

	@staticmethod
	def unblock_access_tracking(prev_computation):
		IncrementalMonitor._pop_current_computation(prev_computation)



	def _add_outgoing_dependency(self, dep):
		if self._outgoing_dependencies is None:
			self._outgoing_dependencies = weakref.WeakKeyDictionary()
		self._outgoing_dependencies[dep] = None

	def _remove_outgoing_dependency(self, dep):
		if self._outgoing_dependencies is not None:
			del self._outgoing_dependencies[dep]
			if len(self._outgoing_dependencies) == 0:
				self._outgoing_dependencies = None
		else:
			raise KeyError





class Test_IncrementalMonitor (unittest.TestCase):
	class _Counter (object):
		def __init__(self):
			self.count = 0

		def __call__(self, *args, **kwargs):
			self.count += 1


	def signal_counter(self):
		return Test_IncrementalMonitor._Counter()



	@staticmethod
	def _get_listeners(inc):
		ls =  []
		if inc._listeners is not None:
			for r in inc._listeners:
				l = r()
				if l is not None:
					ls.append(l)
		return ls


	def test_listener_refs(self):
		inc = IncrementalMonitor()

		l1 = self.signal_counter()
		l2 = self.signal_counter()
		l3 = self.signal_counter()
		l4 = self.signal_counter()


		inc.add_listener(l1)
		inc.add_listener(l2)
		inc.add_listener(l3)
		inc.add_listener(l4)

		del l4
		gc.collect()
		self.assertEqual(set([l1, l2, l3]), set(self._get_listeners(inc)))

		del l3
		gc.collect()
		self.assertEqual(set([l1, l2]), set(self._get_listeners(inc)))

		l3 = self.signal_counter()
		inc.add_listener(l3)
		inc.add_listener(l3)
		self.assertEqual(set([l1, l2, l3]), set(self._get_listeners(inc)))

		del l3
		gc.collect()
		inc.remove_listener(l2)
		self.assertEqual(set([l1]), set(self._get_listeners(inc)))
		self.assertTrue(inc.has_listeners)

		inc.remove_listener(l1)
		self.assertEqual(set(), set(self._get_listeners(inc)))
		self.assertFalse(inc.has_listeners)


		inc.add_listener(l1)
		inc.add_listener(l2)
		del l2
		gc.collect()
		inc._notify_changed()
		self.assertEqual(set([l1]), set(self._get_listeners(inc)))


