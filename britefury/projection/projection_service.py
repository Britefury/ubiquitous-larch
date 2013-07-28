##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.dynamicsegments.service import DynamicPageService
from britefury.projection.incremental_view import IncrementalView
from britefury.projection.subject import Subject
from britefury import command



class CouldNotResolveLocationError (Exception):
	pass



class ProjectionService (DynamicPageService):
	"""
	Projection service

	A dynamic page service that uses the projection system to display objects and resolves locations to
	subjects.

	Commands:
	For each focus object on the subject path from the root to the final subject:
		each focus that defines a __command__ should have it return a list of commands.
		These lists are concatenated and are made available

	Augmenting the page
	It can be desirable to have a containing object be able to place a frame around pages of child objects.
	To do so, add an augment_page attribute to the subject with add_step. This function will be called,
	with the subject as a parameter. It should return a new object that will present as the augmented
	page. A new step will be added to the subject with the focus attribute set to the newly augmented page.
	"""


	def __init__(self, front_page_model):
		super(ProjectionService, self).__init__()
		self.__front_page_model = front_page_model


	def initialise_page(self, dynamic_page, location):
		"""
		Initialise the page
		:param dynamic_page: The page that will display the required content
		:param location: The location which we must resolve to find the content to display
		:return: an IncrementalView
		"""
		focus_steps = []

		if isinstance(location, Subject):
			subject = location
		else:
			subject = self.__resolve_location(location, focus_steps)

		# Augment page
		try:
			augment_page_fn = subject.augment_page
		except AttributeError:
			pass
		else:
			augmented_page = augment_page_fn(subject)
			subject.add_step(focus=augmented_page)

		cmds = []
		for f in reversed(focus_steps):
			try:
				method = f.__commands__
			except AttributeError:
				pass
			else:
				cmds.extend(method())

		command_set = command.CommandSet(cmds)
		command_set.attach_to_page(dynamic_page)

		# Create the incremental view
		return IncrementalView(subject, dynamic_page)



	def __focus_step(self, steps, focus):
		"""
		Adds :param focus: to :param steps: if it is not already there
		:param steps: a list of focii
		:param focus: a focus
		:return: None
		"""
		if focus not in steps:
			steps.append(focus)

	def __resolve_step(self, model, subject, focus_steps):
		"""
		Steps the subject forward by invoking __resolve_self__ on :param model: if it is available.
		This will be performed again on the returned result, until the result is the same as the target
		(__resolve_self__ returns self).

		:param model: The starting model
		:param subject: The subject
		:param focus_steps: A list of focii
		:return: The new model
		"""
		while True:
			self.__focus_step(focus_steps, model)
			try:
				__resolve_self__ = model.__resolve_self__
			except AttributeError:
				break
			m = __resolve_self__(subject)
			if m is model:
				break
			model = m
		return model

	def __resolve_name(self, model, subject, name):
		"""
		:param model: The starting model
		:param subject: The subject
		:param name: The name to look up
		:return: The result of invoking model.__resolve__(:param name:, :param subject:) or None if __resolve__ is not defined
		"""
		try:
			__resolve__ = model.__resolve__
		except AttributeError:
			return None
		return __resolve__(name, subject)

	def __resolve_location(self, location, focus_steps):
		"""
		Resolves a location

		:param location: A location to resolve
		:param focus_steps: A list that is modified to contain the list of focii along the path to the resulting subject
		:return: The subject identified by :param location:
		"""
		subject = Subject()
		subject.add_step(focus=self.__front_page_model, location_trail=['pages'], perspective=None, title='Service front page')
		if location is None  or  location == '':
			self.__resolve_step(self.__front_page_model, subject, focus_steps)
			return subject
		else:
			m = self.__front_page_model
			m = self.__resolve_step(m, subject, focus_steps)
			for n in location.split('/'):
				m = self.__resolve_name(m, subject, n)
				self.__focus_step(focus_steps, m)
				if m is None:
					raise CouldNotResolveLocationError, 'Could not resolve \'{0}\' in location \'{1}\''.format(n, location)
				m = self.__resolve_step(m, subject, focus_steps)
				if m is None:
					raise CouldNotResolveLocationError, 'Could not resolve \'{0}\' in location \'{1}\''.format(n, location)
			return subject
