##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
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
