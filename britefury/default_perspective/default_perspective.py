##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************

from britefury.projection.object_pres_perspective import ObjectPresPerspective


class DefaultPerspective (ObjectPresPerspective):
	__present_method_name__ = '__present__'


DefaultPerspective.instance = DefaultPerspective()


