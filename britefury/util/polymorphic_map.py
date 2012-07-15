##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************


class PolymorphicMap (object):
	def __init__(self, map={}):
		self.__map = {}
		self.__map.update(map)
		self.__map_cache = None



	def __getitem__(self, cls):
		self.__update_cache()
		try:
			return self.__map_cache[cls]
		except KeyError:
			try:
				bases = cls.mro()
			except TypeError:
				raise KeyError

			for base in bases:
				if base in self.__map_cache:
					x = self.__map_cache[base]
					self.__map_cache[cls] = x
					return x
			raise

	def __setitem__(self, key, value):
		self.__map[key] = value
		self.__map_cache = None



	def for_instance(self, x):
		return self[type(x)]




	def __update_cache(self):
		if self.__map_cache is None:
			self.__map_cache = {}
			self.__map_cache.update(self.__map)