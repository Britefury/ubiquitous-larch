##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.core.dynamicpage.service import DynamicPageService
from larch.core.incremental_view import IncrementalView
from larch.core.subject import Subject
from larch import command


class CouldNotResolveLocationError (Exception):
	pass



class ProjectionService (DynamicPageService):
	"""
	Projection service

	A dynamic page service that uses the core system to display objects and resolves locations to
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

	The locations 'pages' and 'pages/' resolve to the front page
	"""


	def __init__(self, front_page_model):
		"""
		Constructor

		:param front_page_model - the front page
		:return: ProjectionService instance
		"""
		super(ProjectionService, self).__init__()
		self.__front_page_model = front_page_model


	def page(self, doc_url, location='', get_params=None, user=None):
		view = self.new_view(doc_url, location, get_params, user=user)
		subject = self.__resolve_location(doc_url, location)

		# Augment page
		self.__augment_page(subject)

		# Attach commands
		self.__attach_commands(view, subject)

		# Create the incremental view and attach as view data
		view.view_data = IncrementalView(subject, view.dynamic_page)

		return view.dynamic_page.page_html()



	def page_for_subject(self, doc_url, subject, location='', get_params=None, user=None):
		view = self.new_view(doc_url, location, get_params, user=user)

		# Augment page
		self.__augment_page(subject)

		# Attach commands
		self.__attach_commands(view, subject)

		# Create the incremental view and attach as view data
		view.view_data = IncrementalView(subject, view.dynamic_page)

		return view.dynamic_page.page_html()



	def kernel_message(self, message, *args, **kwargs):
		return self.__front_page_model.kernel_message(message, *args, **kwargs)





	def __resolve_step(self, model, subject):
		"""
		Steps the subject forward by invoking __resolve_self__ on :param model: if it is available.
		This will be performed again on the returned result, until the result is the same as the target
		(__resolve_self__ returns self).

		:param model: The starting model
		:param subject: The subject
		:return: The new model
		"""
		while True:
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

	def __resolve_location(self, root_url, location):
		"""
		Resolves a location

		:param location: A location to resolve
		:param focus_steps: A list that is modified to contain the list of focii along the path to the resulting subject
		:return: The subject identified by :param location:
		"""
		subject = Subject()
		subject.add_step(focus=self.__front_page_model, location_trail=['pages', root_url], perspective=None, title='Service front page')
		if location == '':
			self.__resolve_step(self.__front_page_model, subject)
			return subject
		else:
			m = self.__front_page_model
			m = self.__resolve_step(m, subject)
			for n in location.split('/'):
				m = self.__resolve_name(m, subject, n)
				if m is None:
					raise CouldNotResolveLocationError, 'Could not resolve \'{0}\' in location \'{1}\''.format(n, location)
				m = self.__resolve_step(m, subject)
				if m is None:
					raise CouldNotResolveLocationError, 'Could not resolve \'{0}\' in location \'{1}\''.format(n, location)
			return subject


	def __augment_page(self, subject):
		# Augment page
		try:
			augment_page_fn = subject.augment_page
		except AttributeError:
			pass
		else:
			augmented_page = augment_page_fn(subject)
			subject.add_step(focus=augmented_page)


	def __attach_commands(self, view, subject):
		cmds = []
		for f in subject.focii:
			try:
				method = f.__commands__
			except AttributeError:
				pass
			else:
				cmds.extend(method(view.dynamic_page.public_api))

		command_set = command.CommandSet(cmds)
		command_set.attach_to_page(view.dynamic_page)
