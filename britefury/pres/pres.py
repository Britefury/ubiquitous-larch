##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************
from britefury.pres.presctx import PresentationContext



class Pres (object):
	def build(self, pres_ctx):
		raise NotImplementedError, 'abstract'


	@staticmethod
	def map_build(pres_ctx, xs):
		return [x.build(pres_ctx)   for x in xs]


	@staticmethod
	def coerce(x):
		if x is None:
			return None
		elif isinstance(x, Pres):
			return x
		else:
			return InnerFragment(x)


	@staticmethod
	def coerce_not_none(x):
		if x is None:
			return InnerFragment(None)
		elif isinstance(x, Pres):
			return x
		else:
			return InnerFragment(x)


	@staticmethod
	def map_coerce(xs):
		return [Pres.coerce(x)   for x in xs]

	@staticmethod
	def map_coerce_not_none(xs):
		return [Pres.coerce_not_none(x)   for x in xs]



class ApplyPerspective (Pres):
	def __init__(self, perspective, child):
		self.__perspective = perspective
		self.__child = Pres.coerce_not_none(child)


	def build(self, pres_ctx):
		return self.__child.build(PresentationContext(pres_ctx.fragment_view, self.__perspective, pres_ctx.inherited_state))



class InnerFragment (Pres):
	def __init__(self, model):
		self.__model = model


	def build(self, pres_ctx):
		fragment_view = pres_ctx.fragment_view
		inherited_state = pres_ctx.inherited_state
		return fragment_view.present_inner_fragment(self.__model, pres_ctx.perspective, inherited_state)


