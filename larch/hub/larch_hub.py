##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import uuid

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



class KernelInterface (object):
	def kernel_message(self, doc_category, doc_name, message, *args, **kwargs):
		raise NotImplementedError, 'abstract'

	def new_kernel(self, on_created, service_constructor, *service_cons_args, **service_cons_kwargs):
		raise NotImplementedError, 'abstract'

	def map_category_and_name_to_kernel(self, doc_category, doc_name, service_id):
		raise NotImplementedError, 'abstract'

	def get_service_id(self, doc_category, doc_name):
		raise NotImplementedError, 'abstract'




class LarchDefaultHub (AbstractLarchHub, KernelInterface):
	def __init__(self):
		AbstractLarchHub.__init__(self)
		KernelInterface.__init__(self)
		self.__services = {}
		self.__category_and_name_to_service_id = {}


	def kernel_message(self, doc_category, doc_name, message, *args, **kwargs):
		service_id = self.get_service_id(doc_category, doc_name)
		service = self.__services[service_id]
		return service.kernel_message(message, *args, **kwargs)


	def new_kernel(self, on_created, service_constructor, *service_cons_args, **service_cons_kwargs):
		service_id = uuid.uuid4()
		service = service_constructor(self, *service_cons_args, **service_cons_kwargs)
		self.__services[service_id] = service
		on_created(service_id)


	def map_category_and_name_to_kernel(self, doc_category, doc_name, service_id):
		service_name = doc_category, doc_name
		self.__category_and_name_to_service_id[service_name] = service_id

	def get_service_id(self, doc_category, doc_name):
		service_name = doc_category, doc_name
		return self.__category_and_name_to_service_id.get(service_name)


	def page(self, doc_category, doc_name, location='', get_params=None, user=None):
		service_id = self.get_service_id(doc_category, doc_name)
		if service_id is not None:
			service = self.__services.get(service_id)
			return service.page('{0}/{1}'.format(doc_category, doc_name), location, get_params, user)
		else:
			raise CouldNotResolveLocationError

	def event(self, doc_category, doc_name, view_id, data):
		service_id = self.get_service_id(doc_category, doc_name)
		service = self.__services.get(service_id)
		return service.event(view_id, data)   if service is not None   else None

	def form(self, doc_category, doc_name, view_id, form_data):
		service_id = self.get_service_id(doc_category, doc_name)
		service = self.__services.get(service_id)
		return service.form(view_id, form_data)   if service is not None   else None

	def resource(self, doc_category, doc_name, view_id, rsc_id):
		service_id = self.get_service_id(doc_category, doc_name)
		service = self.__services.get(service_id)
		return service.resource(view_id, rsc_id)   if service is not None   else None


def start_hub_and_client(main_doc_category, main_doc_name, main_constructor, *main_cons_args, **main_cons_kwargs):
	def on_created(service_id):
		hub.map_category_and_name_to_kernel(main_doc_category, main_doc_name, service_id)

	hub = LarchDefaultHub()
	hub.new_kernel(on_created, main_constructor, *main_cons_args, **main_cons_kwargs)
	return hub
