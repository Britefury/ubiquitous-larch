##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.dynamicsegments.service import DynamicDocumentService
from britefury.incremental_view.incremental_view import IncrementalView



class CouldNotResolveLocationError (Exception):
	pass



class ProjectionService (DynamicDocumentService):
	def __init__(self, front_page_subject):
		super(ProjectionService, self).__init__()
		self.__front_page_subject = front_page_subject


	def initialise_session(self, dynamic_document, location):
		subject = self.__resolve_location(location)

		# Create the incremental view
		return IncrementalView(subject, dynamic_document)




	def __resolve_location(self, location):
		if location is None  or  location == '':
			return self.__front_page_subject
		else:
			s = self.__front_page_subject
			for n in location.split('/'):
				s = s.__resolve__(n)
				if s is None:
					raise CouldNotResolveLocationError, 'Could not resolve \'{0}\' in location \'{1}\''.format(n, location)
			return s
