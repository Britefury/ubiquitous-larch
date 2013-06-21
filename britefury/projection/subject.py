##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.default_perspective.default_perspective import DefaultPerspective



class Subject (object):
	class __NoInitialValue (object):
		pass

	__NoInitialValue.instance = __NoInitialValue()

	def __init__(self):
		self.__steps = []



	@property
	def perspective(self):
		p = self.get_attr('perspective')
		return DefaultPerspective.instance   if p is None   else p


	@property
	def location(self):
		trail = self.reduce('location_trail', lambda cumulative, t: t + cumulative, [])
		return '/' + '/'.join(trail)



	def add_step(self, **attributes):
		"""Add a step to the subject
		"""
		self.__steps.append(attributes)


	def get_attr(self, item):
		"""Get a named attribute

		item - the name of the attribute
		"""
		for step in reversed(self.__steps):
			try:
				return step[item]
			except KeyError:
				pass
		raise AttributeError, 'Subject has no attribute {0}'.format(item)


	def __getattr__(self, item):
		"""Get a named attribute

		item - the name of the attribute
		"""
		return self.get_attr(item)


	def reduce(self, item, reduce_fn, initial_value=__NoInitialValue.instance):
		"""Accumulate values of a named attribute by reduction

		item - the name of the attribute
		reduce_fn - a reduction function of the form function(cumulative_value, value) -> cumulative_value

		Note that the direction proceeds from tip to root
		"""
		for step in reversed(self.__steps):
			try:
				value = step[item]
			except KeyError:
				continue

			if initial_value is self.__NoInitialValue.instance:
				initial_value = value
			else:
				initial_value = reduce_fn(initial_value, value)

		if initial_value is self.__NoInitialValue.instance:
			raise AttributeError, 'Subject has no attribute {0}'.format(item)
		else:
			return initial_value


