##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
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

		matplotlib.use('module://larch.hooks.matplotlib.backend_larch')

		# Hack pyplot to make show() return something

		if not __pyplot_hacked:
			__pyplot_hacked = True

			from matplotlib import pyplot

			def __pyplot_show(*args, **kwargs):
				return pyplot._show(*args, **kwargs)

			pyplot.show = __pyplot_show


