##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.projection.object_pres_perspective import ObjectPresPerspective
from britefury.inspector.inspector import InspectorPerspective
from britefury.inspector.present_exception import present_exception_no_traceback


class DefaultPerspective (ObjectPresPerspective):
	__present_method_name__ = '__present__'
	__fallback_perspective__ = InspectorPerspective.instance


DefaultPerspective.instance = DefaultPerspective()


@DefaultPerspective.instance.presenter(Exception)
def present_exception(model, fragment_view):
	return present_exception_no_traceback(model)
