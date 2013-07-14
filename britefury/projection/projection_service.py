##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.dynamicsegments.service import DynamicDocumentService
from britefury.incremental_view.incremental_view import IncrementalView
from britefury.projection.subject import Subject
from britefury import command



class CouldNotResolveLocationError (Exception):
	pass



class ProjectionService (DynamicDocumentService):
	def __init__(self, front_page_model):
		super(ProjectionService, self).__init__()
		self.__front_page_model = front_page_model


	def initialise_session(self, dynamic_document, location):
		focus_steps = []

		if isinstance(location, Subject):
			subject = location
		else:
			subject = self.__resolve_location(location, focus_steps)

		cmds = []
		for f in reversed(focus_steps):
			try:
				method = f.__commands__
			except AttributeError:
				pass
			else:
				cmds.extend(method())

		command_set = command.CommandSet(cmds)
		command_set.attach_to_document(dynamic_document)

		# Create the incremental view
		return IncrementalView(subject, dynamic_document)



	def __focus_step(self, steps, focus):
		if focus not in steps:
			steps.append(focus)

	def __resolve_step(self, model, subject, focus_steps):
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
		try:
			__resolve__ = model.__resolve__
		except AttributeError:
			return None
		return __resolve__(name, subject)

	def __resolve_location(self, location, focus_steps):
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
