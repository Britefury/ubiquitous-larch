##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.default_perspective.default_perspective import DefaultPerspective


class Subject (object):
	def __init__(self, enclosing_subject, focus, perspective=DefaultPerspective.instance, title=None):
		self.__enclosing_subject = enclosing_subject
		self.__focus = focus
		self.__perspective = perspective
		self.__title = title


	def __getattr__(self, item):
		s = self.__enclosing_subject
		while s is not None:
			try:
				return s.__dict__[item]
			except KeyError:
				pass
			s = s.enclosing_subject
		raise AttributeError, 'Subject {0} has no attribute {1}'.format(self, item)


	@property
	def enclosing_subject(self):
		return self.__enclosing_subject

	@property
	def focus(self):
		return self.__focus

	@property
	def perspective(self):
		return self.__perspective

	@property
	def title(self):
		return self.__title



	def __resolve__(self, name):
		return None

	def resolve(self, location):
		if location is None  or  location == '':
			return self
		else:
			s = self
			for n in location.split('/'):
				s = s.__resolve__(n)
				if s is None:
					return

