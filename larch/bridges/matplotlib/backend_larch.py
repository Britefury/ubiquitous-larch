##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
"""
Ubiquitous Larch matplotlib backend

Written while referring to the Web-Agg backend in matplotlib

"""

try:
	from matplotlib.backends import backend_agg
	import numpy as np
except ImportError:
	backend_agg = None


if backend_agg is not None:
	from matplotlib import backend_bases
	from matplotlib.figure import Figure
	from matplotlib._pylab_helpers import Gcf
	from matplotlib import _png
	from britefury.pres import resource
	import io



	def new_figure_manager(num, *args, **kwargs):
		"""
		Create a new figure manager instance
		"""
		FigureClass = kwargs.pop('FigureClass', Figure)
		this_fig = FigureClass(*args, **kwargs)
		return new_figure_manager_given_figure(num, this_fig)


	def new_figure_manager_given_figure(num, figure):
		"""
		Create a new figure manager instance for the given figure.
		"""
		canvas = FigureCanvasLarchAgg(figure)
		manager = FigureManagerLarchAgg(canvas, num)
		return manager



	class FigureCanvasLarchAgg (backend_agg.FigureCanvasAgg):
		def __init__(self, *args, **kwargs):
			backend_agg.FigureCanvasAgg.__init__(self, *args, **kwargs)
			self._buffer = io.BytesIO()



		def show(self):
			self._buffer.truncate()
			self._buffer.seek(0)

			self.draw()
			renderer = self.get_renderer()

			_png.write_png(renderer._renderer.buffer_rgba(), renderer.width, renderer.height, self._buffer)

			data = self._buffer.getvalue()

			img = resource.ImageFromBinary(data, 'image/png', renderer.width, renderer.height)
			return img




	class FigureManagerLarchAgg (backend_bases.FigureManagerBase):
		def __init__(self, canvas, num):
			backend_bases.FigureManagerBase.__init__(self, canvas, num)

		def show(self):
			x = self.canvas.show()
			return x



	def show(block=None):
		"""
		Show the current figure

		block argument is ignred
		"""
		manager = Gcf.get_active()
		if manager is not None:
			return manager.show()
		else:
			return None



