##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
try:
	import matplotlib
except ImportError:
	def init():
		pass
else:
	__pyplot_hacked = False

	def init():
		global __pyplot_hacked

		matplotlib.use('module://larch.bridges.matplotlib.backend_larch')

		# Hack pyplot to make show() return something

		if not __pyplot_hacked:
			__pyplot_hacked = True

			from matplotlib import pyplot

			def __pyplot_show(*args, **kwargs):
				return pyplot._show(*args, **kwargs)

			pyplot.show = __pyplot_show


