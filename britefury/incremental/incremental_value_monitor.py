##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.incremental import incremental_monitor


class IncrementalValueMonitor (incremental_monitor.IncrementalMonitor):
	def on_access(self):
		self._notify_refreshed()
		self._on_value_access()

	def on_changed(self):
		self._notify_changed()





class Test_IncrementalValueMonitor (incremental_monitor.Test_IncrementalMonitor):
	def test_listener(self):
		counter = self.signal_counter()
		self.assertEqual(0, counter.count)

		inc = IncrementalValueMonitor()

		inc.add_listener(counter)

		inc.on_changed()
		self.assertEqual(1, counter.count)

		inc.on_changed()
		self.assertEqual(1, counter.count)

		inc.on_access()
		inc.on_changed()
		self.assertEqual(2, counter.count)

