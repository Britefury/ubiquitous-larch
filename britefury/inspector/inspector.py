##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.projection.abstract_perspective import AbstractPerspective
from britefury.inspector.llinspector import llinspect
from britefury.inspector.present_primitive import present_primitive
from britefury.inspector.present_python import present_python


class InspectorPerspective (AbstractPerspective):
	def present_model(self, model, fragment_view, inherited_state):

		p = present_primitive(model)
		if p is not None:
			return p

		p = present_python(model)
		if p is not None:
			return p

		return llinspect.present_object(model, fragment_view, inherited_state)


InspectorPerspective.instance = InspectorPerspective()

inspect = InspectorPerspective.instance
