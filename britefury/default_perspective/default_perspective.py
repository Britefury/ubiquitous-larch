##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.projection.object_pres_perspective import ObjectPresPerspective
from britefury.inspector.inspector import InspectorPerspective


class DefaultPerspective (ObjectPresPerspective):
	__present_method_name__ = '__present__'
	__fallback_perspective__ = InspectorPerspective.instance


DefaultPerspective.instance = DefaultPerspective()


