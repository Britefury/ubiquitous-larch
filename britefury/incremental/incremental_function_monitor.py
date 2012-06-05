##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************
__author__ = 'Geoff'

import gc

from britefury.incremental import incremental_monitor




class IncrementalEvaluationCycleError (Exception):
	pass





class IncrementalFunctionMonitor (incremental_monitor.IncrementalMonitor):
	_FLAG_CYCLE_LOCK = 0x1
	_FLAG_BLOCK_INCOMING_DEPENDENCIES = 0x2

	def __init__(self, owner=None):
		super(IncrementalFunctionMonitor, self).__init__(owner)
		self._incoming_dependencies = None
		self.__flags = 0


	incoming_dependencies = property(lambda self: (self._incoming_dependencies   if self._incoming_dependencies is not None   else set()))


	def on_access(self):
		self._on_value_access()

	def on_changed(self):
		self._notify_changed()

	def block_and_clear_incoming_dependencies(self):
		self.__set_flag(self._FLAG_BLOCK_INCOMING_DEPENDENCIES)
		self._incoming_dependencies = None


	def on_refresh_begin(self):
		if self.__test_flag(self._FLAG_CYCLE_LOCK):
			raise IncrementalEvaluationCycleError

		self.__clear_flag(self._FLAG_BLOCK_INCOMING_DEPENDENCIES)
		self.__set_flag(self._FLAG_CYCLE_LOCK)

		if self._incremental_state != incremental_monitor.IncrementalMonitor.REFRESH_NOT_REQUIRED:
			# Push current computation
			old_computation = incremental_monitor.IncrementalMonitor._push_current_computation(self)

			refresh_state = old_computation, self._incoming_dependencies
			self._incoming_dependencies = None
			return refresh_state
		else:
			return None


	def on_refresh_end(self, refresh_state):
		if self._incremental_state != incremental_monitor.IncrementalMonitor.REFRESH_NOT_REQUIRED:
			old_computation, prev_incoming_dependencies = refresh_state

			# Restore current computation
			incremental_monitor.IncrementalMonitor._pop_current_computation(old_computation)

			# Disconnect the dependencies that are being removed
			if prev_incoming_dependencies is not None:
				for inc in prev_incoming_dependencies:
					if self._incoming_dependencies is None  or  inc not in self._incoming_dependencies:
						inc._remove_outgoing_dependency(self)

			# Connect new dependencies
			if self._incoming_dependencies is not None:
				for inc in self._incoming_dependencies:
					if prev_incoming_dependencies is None  or  inc not in prev_incoming_dependencies:
						inc._add_outgoing_dependency(self)


			self._incremental_state = incremental_monitor.IncrementalMonitor.REFRESH_NOT_REQUIRED

		self.__clear_flag(self._FLAG_CYCLE_LOCK)


	def _on_incoming_dependency_access(self, inc):
		self._add_incoming_dependency(inc)


	def _add_incoming_dependency(self, dep):
		if not self.__test_flag(self._FLAG_BLOCK_INCOMING_DEPENDENCIES):
			if self._incoming_dependencies is None:
				self._incoming_dependencies = set()
			self._incoming_dependencies.add(dep)





	#
	#
	# Flags
	#
	#

	def __clear_flag(self, flag):
		self.__flags &= ~flag


	def __set_flag(self, flag):
		self.__flags |= flag


	def __set_flag_value(self, flag, value):
		if value:
			self.__flags |= flag
		else:
			self.__flags &= ~flag


	def __test_flag(self, flag):
		return (self.__flags & flag) != 0






class Test_IncrementalFunctionMonitor (incremental_monitor.Test_IncrementalMonitor):
	def test_listener(self):
		counter = self.signal_counter()
		self.assertEqual(0, counter.count)

		inc = IncrementalFunctionMonitor()

		inc.add_listener(counter)

		inc.on_changed()
		self.assertEqual(1, counter.count)

		inc.on_changed()
		self.assertEqual(1, counter.count)

		refresh_state = inc.on_refresh_begin()
		inc.on_refresh_end(refresh_state)
		inc.on_changed()
		self.assertEqual(2, counter.count)





	def test_chain(self):
		inc1 = IncrementalFunctionMonitor()
		inc2 = IncrementalFunctionMonitor()
		inc3 = IncrementalFunctionMonitor()
		inc4 = IncrementalFunctionMonitor()

		l1 = self.signal_counter()
		l2 = self.signal_counter()
		l3 = self.signal_counter()
		l4 = self.signal_counter()
		inc1.add_listener(l1)
		inc2.add_listener(l2)
		inc3.add_listener(l3)
		inc4.add_listener(l4)

		rs1 = inc1.on_refresh_begin()
		inc1.on_refresh_end( rs1 )
		inc1.on_changed()
		self.assertEqual( 1, l1.count )

		rs2 = inc2.on_refresh_begin()
		rs1 = inc1.on_refresh_begin()
		inc1.on_refresh_end( rs1 )
		inc1.on_access()
		inc2.on_refresh_end( rs2 )

		self.assertEqual( set([inc2]), inc1.outgoing_dependences )
		self.assertEqual( set([inc1]), inc2.incoming_dependencies )

		rs3 = inc3.on_refresh_begin()
		inc2.on_access()
		inc3.on_refresh_end( rs3 )

		self.assertEqual( set([inc3]), inc2.outgoing_dependences )
		self.assertEqual( set([inc2]), inc3.incoming_dependencies )

		rs4 = inc4.on_refresh_begin()
		inc2.on_access()
		inc4.on_refresh_end( rs4 )

		self.assertEqual( set([inc3, inc4]), inc2.outgoing_dependences )
		self.assertEqual( set([inc2]), inc4.incoming_dependencies )


		inc1.on_changed()
		self.assertEqual( 2, l1.count )
		self.assertEqual( 1, l2.count )
		self.assertEqual( 1, l3.count )
		self.assertEqual( 1, l4.count )

		rs1 = inc1.on_refresh_begin()
		inc1.on_refresh_end( rs1 )
		inc1.on_changed()
		self.assertEqual( 3, l1.count )
		self.assertEqual( 1, l2.count )
		self.assertEqual( 1, l3.count )
		self.assertEqual( 1, l4.count )

		rs4 = inc4.on_refresh_begin()
		rs2 = inc2.on_refresh_begin()
		rs1 = inc1.on_refresh_begin()
		inc1.on_refresh_end( rs1 )
		inc1.on_access()
		inc2.on_refresh_end( rs2 )
		inc2.on_access()
		inc4.on_refresh_end( rs4 )
		rs3 = inc3.on_refresh_begin()
		inc2.on_access()
		inc3.on_refresh_end( rs3 )

		self.assertEqual( set([inc2]), inc1.outgoing_dependences )
		self.assertEqual( set([inc3, inc4]), inc2.outgoing_dependences )
		self.assertEqual( set(), inc3.outgoing_dependences )
		self.assertEqual( set(), inc4.outgoing_dependences )
		self.assertEqual( set(),  inc1.incoming_dependencies )
		self.assertEqual( set([inc1]), inc2.incoming_dependencies )
		self.assertEqual( set([inc2]), inc3.incoming_dependencies )
		self.assertEqual( set([inc2]), inc4.incoming_dependencies )

		inc1.on_changed()
		self.assertEqual( 4, l1.count )
		self.assertEqual( 2, l2.count )
		self.assertEqual( 2, l3.count )
		self.assertEqual( 2, l4.count )



	def test_block_access_tracking(self):
		inc1 = IncrementalFunctionMonitor()
		inc2 = IncrementalFunctionMonitor()
		inc3 = IncrementalFunctionMonitor()
		inc4 = IncrementalFunctionMonitor()

		l1 = self.signal_counter()
		l2 = self.signal_counter()
		l3 = self.signal_counter()
		l4 = self.signal_counter()
		inc1.add_listener(l1)
		inc2.add_listener(l2)
		inc3.add_listener(l3)
		inc4.add_listener(l4)


		rs4 = inc4.on_refresh_begin()
		rs2 = inc2.on_refresh_begin()
		rs1 = inc1.on_refresh_begin()
		inc1.on_refresh_end( rs1 )
		inc1.on_access()
		inc2.on_refresh_end( rs2 )
		inc2.on_access()
		inc4.on_refresh_end( rs4 )
		rs3 = inc3.on_refresh_begin()
		f = incremental_monitor.IncrementalMonitor.block_access_tracking()
		inc2.on_access()
		incremental_monitor.IncrementalMonitor.unblock_access_tracking( f )
		inc3.on_refresh_end( rs3 )

		self.assertEqual(set([inc2]), inc1.outgoing_dependences )
		self.assertEqual(set([inc4]), inc2.outgoing_dependences )
		self.assertEqual(set(), inc3.outgoing_dependences )
		self.assertEqual(set(), inc4.outgoing_dependences )
		self.assertEqual(set(), inc1.incoming_dependencies )
		self.assertEqual(set([inc1]), inc2.incoming_dependencies )
		self.assertEqual(set(), inc3.incoming_dependencies )
		self.assertEqual(set([inc2]), inc4.incoming_dependencies )

		inc1.on_changed()
		self.assertEqual(1, l1.count )
		self.assertEqual(1, l2.count )
		self.assertEqual(0, l3.count )
		self.assertEqual(1, l4.count )



	def test_cycle(self):
		inc1 = IncrementalFunctionMonitor()

		rs1 = inc1.on_refresh_begin()

		def _cycle():
			inc1.on_refresh_begin()

		self.assertRaises(IncrementalEvaluationCycleError, _cycle)

		inc1.on_refresh_end( rs1 )



	def test_unnecessary_refresh(self):
		# This test is for coverage purposes only
		inc1 = IncrementalFunctionMonitor()

		rs1 = inc1.on_refresh_begin()
		inc1.on_refresh_end( rs1 )

		# Another refresh, without sending an 'on_changed'
		rs1 = inc1.on_refresh_begin()
		inc1.on_refresh_end( rs1 )

		

	def test_deps(self):
		inc1 = IncrementalFunctionMonitor()
		inc2 = IncrementalFunctionMonitor()
		inc3 = IncrementalFunctionMonitor()
		inc4 = IncrementalFunctionMonitor()

		rs4 = inc4.on_refresh_begin()
		rs3 = inc3.on_refresh_begin()
		rs2 = inc2.on_refresh_begin()
		rs1 = inc1.on_refresh_begin()
		inc1.on_refresh_end( rs1 )
		inc1.on_access()
		inc2.on_refresh_end( rs2 )
		inc2.on_access()
		inc3.on_refresh_end( rs3 )
		inc3.on_access()
		inc4.on_refresh_end( rs4 )


		self.assertEqual(set([inc2]), inc1.outgoing_dependences )
		self.assertEqual(set([inc3]), inc2.outgoing_dependences )
		self.assertEqual(set([inc4]), inc3.outgoing_dependences )
		self.assertEqual(set(), inc4.outgoing_dependences )
		self.assertEqual(set(), inc1.incoming_dependencies )
		self.assertEqual(set([inc1]), inc2.incoming_dependencies )
		self.assertEqual(set([inc2]), inc3.incoming_dependencies )
		self.assertEqual(set([inc3]), inc4.incoming_dependencies )

		inc4.on_changed()
		rs4 = inc4.on_refresh_begin()
		inc4.on_refresh_end( rs4 )

		self.assertEqual(set([inc2]), inc1.outgoing_dependences )
		self.assertEqual(set([inc3]), inc2.outgoing_dependences )
		self.assertEqual(set(), inc3.outgoing_dependences )
		self.assertEqual(set(), inc4.outgoing_dependences )
		self.assertEqual(set(), inc1.incoming_dependencies )
		self.assertEqual(set([inc1]), inc2.incoming_dependencies )
		self.assertEqual(set([inc2]), inc3.incoming_dependencies )
		self.assertEqual(set(), inc4.incoming_dependencies )

		del inc4
		del rs4
		del rs3
		del rs2
		del rs1
		gc.collect()

		self.assertEqual(set([inc2]), inc1.outgoing_dependences )
		self.assertEqual(set([inc3]), inc2.outgoing_dependences )
		self.assertEqual(set(), inc3.outgoing_dependences )
		self.assertEqual(set(), inc1.incoming_dependencies )
		self.assertEqual(set([inc1]), inc2.incoming_dependencies )
		self.assertEqual(set([inc2]), inc3.incoming_dependencies )

