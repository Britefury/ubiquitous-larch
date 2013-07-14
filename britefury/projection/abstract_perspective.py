##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.pres import Pres, ApplyPerspective


class AbstractPerspective (object):
	def present_model(self, model, fragment_view):
		raise NotImplementedError, 'abstract'


	def present_object(self, x, fragment_view):
		if isinstance(x, Pres):
			return x
		else:
			return self.present_model(x, fragment_view)


	def apply_to(self, x):
		return ApplyPerspective(self, x)

	def __call__(self, x):
		return ApplyPerspective(self, x)
