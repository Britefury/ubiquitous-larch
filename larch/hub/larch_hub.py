##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.core.projection_service import CouldNotResolveLocationError


class AbstractLarchHub (object):
	def page(self, doc_category, doc_name, location='', get_params=None, user=None):
		raise NotImplementedError, 'abstract'

	def event(self, doc_category, doc_name, view_id, data):
		raise NotImplementedError, 'abstract'

	def form(self, doc_category, doc_name, view_id, form_data):
		raise NotImplementedError, 'abstract'

	def resource(self, doc_category, doc_name, view_id, rsc_id):
		raise NotImplementedError, 'abstract'




class LarchDefaultHub (AbstractLarchHub):
	def __init__(self):
		self.__services = {}


	def new_service(self, doc_category, doc_name, service_constructor, *service_cons_args, **service_cons_kwargs):
		k = doc_category, doc_name
		service = service_constructor(*service_cons_args, **service_cons_kwargs)
		self.__services[k] = service

	def page(self, doc_category, doc_name, location='', get_params=None, user=None):
		k = doc_category, doc_name
		service = self.__services.get(k)
		if service is not None:
			return service.page('/{0}/{1}'.format(doc_category, doc_name), location, get_params, user)
		else:
			raise CouldNotResolveLocationError

	def event(self, doc_category, doc_name, view_id, data):
		k = doc_category, doc_name
		service = self.__services.get(k)
		return service.event(view_id, data)   if service is not None   else None

	def form(self, doc_category, doc_name, view_id, form_data):
		k = doc_category, doc_name
		service = self.__services.get(k)
		return service.form(view_id, form_data)   if service is not None   else None

	def resource(self, doc_category, doc_name, view_id, rsc_id):
		k = doc_category, doc_name
		service = self.__services.get(k)
		return service.resource(view_id, rsc_id)   if service is not None   else None


