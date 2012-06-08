##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import inspect
from britefury.projection.abstract_perspective import AbstractPerspective


class ObjectPresPerspective (AbstractPerspective):
	__present_method_name__ = NotImplemented
	__fallback_perspective__ = NotImplemented



	def present_model(self, model, fragment_view, inherited_state):
		if self.__present_method_name__ is NotImplemented:
			raise NotImplementedError, 'object pres perspective {0} appears to be abstract; __present_method_name__ not defined'.format(self)

		result = None

		try:
			present_method = getattr(model, self.__present_method_name__)
		except AttributeError:
			present_method = None

		if present_method is not None and  inspect.ismethod(present_method)  and  present_method.im_self is None:
			# Method is unbound - don't try to invoke
			present_method = None

		if present_method is not None:
			result = present_method(fragment_view, inherited_state)

		if result is None:
			if self.__fallback_perspective__ is NotImplemented:
				raise NotImplementedError, 'object pres perspective {0} appears to be abstract; __fallback_perspective__ not defined'.format(self)
			elif self.__fallback_perspective__ is not None:
				result = self.__fallback_perspective__.present_object(model, fragment_view, inherited_state)
			else:
				raise ValueError, 'Could not present {0}'.format(model)

		return result


