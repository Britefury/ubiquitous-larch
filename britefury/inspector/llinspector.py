##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.projection.abstract_perspective import AbstractPerspective
from britefury.inspector.present_primitive import present_primitive_data


class LLInspectorPerspective (AbstractPerspective):
	def present_model(self, model, fragment_view, inherited_state):
		p = present_primitive_data(model)
		if p is not None:
			return p
		else:
			raise NotImplementedError, 'not implemented low level inspect for types that are not primitive data types'

LLInspectorPerspective.instance = LLInspectorPerspective()

llinspect = LLInspectorPerspective.instance
