##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.inspector import inspector, llinspector

def init_module(mod):
	mod.inspect = inspector.inspect
	mod.llinspect = llinspector.llinspect
