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

	def new_kernel(self, on_created, doc_category, doc_name, service_constructor, *service_cons_args, **service_cons_kwargs):
		raise NotImplementedError, 'abstract'

	def alias_category_and_name(self, new_category, new_name, existing_category, existing_name):
		raise NotImplementedError, 'abstract'




class LarchDefaultHub (AbstractLarchHub, KernelInterface):
	def __init__(self):
		AbstractLarchHub.__init__(self)
		KernelInterface.__init__(self)
		self.__services = {}


	def kernel_message(self, doc_category, doc_name, message, *args, **kwargs):
		service_id = '{0}/{1}'.format(doc_category, doc_name)
		service = self.__services[service_id]
		return service.kernel_message(message, *args, **kwargs)


	def new_kernel(self, on_created, doc_category, doc_name, service_constructor, *service_cons_args, **service_cons_kwargs):
		service_id = '{0}/{1}'.format(doc_category, doc_name)
		service = service_constructor(self, *service_cons_args, **service_cons_kwargs)
		self.__services[service_id] = service
		on_created()


	def alias_category_and_name(self, new_category, new_name, existing_category, existing_name):
		new_service_id = '{0}/{1}'.format(new_category, new_name)
		existing_service_id = '{0}/{1}'.format(existing_category, existing_name)
		self.__services[new_service_id] = self.__services[existing_service_id]


	def page(self, doc_category, doc_name, location='', get_params=None, user=None):
		service_id = '{0}/{1}'.format(doc_category, doc_name)
		if service_id is not None:
			service = self.__services.get(service_id)
			return service.page('{0}/{1}'.format(doc_category, doc_name), location, get_params, user)
		else:
			raise CouldNotResolveLocationError

	def event(self, doc_category, doc_name, view_id, data):
		service_id = '{0}/{1}'.format(doc_category, doc_name)
		service = self.__services.get(service_id)
		return service.event(view_id, data)   if service is not None   else None

	def form(self, doc_category, doc_name, view_id, form_data):
		service_id = '{0}/{1}'.format(doc_category, doc_name)
		service = self.__services.get(service_id)
		return service.form(view_id, form_data)   if service is not None   else None

	def resource(self, doc_category, doc_name, view_id, rsc_id):
		service_id = '{0}/{1}'.format(doc_category, doc_name)
		service = self.__services.get(service_id)
		return service.resource(view_id, rsc_id)   if service is not None   else None


def start_hub_and_client(main_doc_category, main_doc_name, main_constructor, *main_cons_args, **main_cons_kwargs):
	def on_created():
		pass

	hub = LarchDefaultHub()
	hub.new_kernel(on_created, main_doc_category, main_doc_name, main_constructor, *main_cons_args, **main_cons_kwargs)
	return hub
