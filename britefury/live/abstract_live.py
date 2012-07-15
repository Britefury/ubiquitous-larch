##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.pres import Pres, CompositePres, InnerFragment
from britefury.pres.obj_pres import error_box
from britefury.inspector import present_primitive
from britefury.inspector import present_exception


class AbstractLive (CompositePres):
	class __ValuePres (Pres):
		def __init__(self, live):
			self.__live = live

		def build(self, pres_ctx):
			value = None
			pres_ctx.fragment_view.disable_inspector()
			try:
				value = self.__live.value
			except Exception, e:
				exception_view = present_exception.present_exception_no_traceback(e)
				return error_box('Exception during live evaluation', exception_view)

			if value is not None:
				return Pres.coerce(value).build(pres_ctx)
			else:
				return present_primitive.present_none().build(pres_ctx)


	@property
	def incremental_monitor(self):
		raise NotImplementedError, 'abstract'

	def add_listener(self, listener):
		self.incremental_monitor.add_listener(listener)

	def remove_listener(self, listener):
		self.incremental_monitor.remove_listener(listener)



	@property
	def value(self):
		raise NotImplementedError, 'abstract'

	@value.setter
	def value(self, v):
		raise NotImplementedError, 'abstract'

	@property
	def static_value(self):
		raise NotImplementedError, 'abstract'



	def __call__(self):
		return self.value


	def pres(self, pres_ctx):
		return InnerFragment(self.__ValuePres(self))


