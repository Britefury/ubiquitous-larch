##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.incremental.incremental_function_monitor import IncrementalFunctionMonitor
from britefury.live.abstract_live import AbstractLive


class LiveFunction (AbstractLive):
	def __init__(self, fn):
		self.__incr = IncrementalFunctionMonitor(self)
		self.__fn = fn
		self.__value_cache = None



	@property
	def function(self):
		return self.__fn

	@function.setter
	def function(self, f):
		self.__fn = f
		self.__incr.on_changed()




	@property
	def incremental_monitor(self):
		return self.__incr


	@property
	def value(self):
		try:
			self.__refresh_value()
		finally:
			self.__incr.on_access()
		return self.__value_cache

	@value.setter
	def value(self, v):
		self.function = lambda: v

	@property
	def static_value(self):
		self.__refresh_value()
		return self.__value_cache



	def __refresh_value(self):
		refresh_state = self.__incr.on_refresh_begin()
		try:
			if refresh_state is not None:
				self.__value_cache = self.__fn()
		finally:
			self.__incr.on_refresh_end(refresh_state)


