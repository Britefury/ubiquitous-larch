##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.default_perspective.default_perspective import DefaultPerspective


class Subject (object):
	def __init__(self, enclosing_subject, location_trail, focus, perspective=None, title=None):
		if perspective is None:
			perspective = DefaultPerspective.instance
		self.__enclosing_subject = enclosing_subject
		self.__location_trail = location_trail
		self.__focus = focus
		self.__perspective = perspective
		self.__title = title


	def __getattr__(self, item):
		try:
			return getattr(self.__enclosing_subject, item)
		except AttributeError:
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


	@property
	def location(self):
		subj = self
		trail = []
		while subj is not None:
			trail = list(subj.__location_trail[:]) + trail
			subj = subj.__enclosing_subject
		return '/' + '/'.join(trail)

	def _location_trail_entries(self):
		return None



	def __resolve__(self, name):
		return None



	@staticmethod
	def subject_for(enclosing_subject, location_trail, focus, perspective=None):
		return focus.__subject__(enclosing_subject, location_trail, perspective)

