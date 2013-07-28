##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.incremental import IncrementalValueMonitor
from britefury.live.abstract_live import AbstractLive


class LiveValue (AbstractLive):
	def __init__(self, value=None):
		self.__incr = IncrementalValueMonitor(self)
		self.__value = value



	@property
	def incremental_monitor(self):
		return self.__incr


	@property
	def value(self):
		self.__incr.on_access()
		return self.__value

	@value.setter
	def value(self, v):
		self.__value = v
		self.__incr.on_changed()

	@property
	def static_value(self):
		return self.__value
