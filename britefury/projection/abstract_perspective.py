##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.pres import Pres, ApplyPerspective


class AbstractPerspective (object):
	def present_model(self, model, fragment_view, inherited_state):
		raise NotImplementedError, 'abstract'


	def present_object(self, x, fragment_view, inherited_state):
		if isinstance(x, Pres):
			return x
		else:
			return self.present_model(x, fragment_view, inherited_state)


	def apply_to(self, x):
		return ApplyPerspective(self, x)

	def __call__(self, x):
		return ApplyPerspective(self, x)
