##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html
from larch.pres.pres import CompositePres
from larch.pres.resource import MessageChannel


class slider(CompositePres):
	def __init__(self, release_fn=None, slide_fn=None, width=None, value=None, min=None, max=None, step=None,
		     orientation=None, animate=False, disabled=False):
		"""
		Create a JQuery UI slider

		:param release_fn: a function to be invoked when the user releases the slider, of the form function(value)
		:param slide_fn: a function to be invoked when the user drags the slider, of the form function(value)
		:param width: the width of the slider, specified as a CSS value e.g. 200px (200 pixels) or 50%, or as an integer value that will be converted to pixels
		:param value: the initial value
		:param min: the minimum value
		:param max: the maximum value
		:param step: the size of steps between positions on the slider
		:param orientation: either 'horizontal' or 'vertical'
		:param animate: if True, or if a numeric value in milliseconds specifying the animation length, this will cause the slider to animate when the user clicks to position it directly
		:param disabled: if True, causes the slider to appear disabled
		:return: the slider control
		"""
		self.__release_fn = release_fn
		self.__slide_fn = slide_fn
		self.__channel = MessageChannel()

		self.__width = '{0}px'.format(width) if isinstance(width, int) or isinstance(width, long)   else width

		options = {}
		if value is not None:
			options['value'] = value
		if min is not None:
			options['min'] = min
		if max is not None:
			options['max'] = max
		if step is not None:
			options['step'] = step
		if orientation is not None:
			options['orientation'] = orientation
		if animate is not False:
			options['animate'] = animate
		if disabled:
			options['disabled'] = True

		self.__options = options


	def __on_change(self, event_name, ev_data):
		if self.__release_fn is not None:
			self.__release_fn(ev_data)

	def __on_slide(self, event_name, ev_data):
		self.__slide_fn(ev_data)


	def set_value(self, value):
		self.__channel.send(value)


	def pres(self, pres_ctx):
		if self.__width is None:
			div = Html('<div></div>')
		else:
			div = Html('<div style="width: {0};"></div>'.format(self.__width))
		div = div.js_function_call('larch.controls.initSlider', self.__slide_fn is not None, self.__options, self.__channel)
		div = div.with_event_handler("slider_change", self.__on_change)
		if self.__slide_fn is not None:
			div = div.with_event_handler("slider_slide", self.__on_slide)
		div = div.use_js('/static/larch_ui.js').use_css('/static/larch_ui.css')
		return div



class range_slider (CompositePres):
	def __init__(self, release_fn=None, slide_fn=None, width=None, values=None, min=None, max=None, step=None,
		 orientation=None, animate=False, disabled=False):
		"""
		Create a JQuery UI slider - with the range option enabled

		:param release_fn: a function to be invoked when the user releases the slider, of the form function(value)
		:param slide_fn: a function to be invoked when the user drags the slider, of the form function(value)
		:param width: the width of the slider, specified as a CSS value e.g. 200px (200 pixels) or 50%, or as an integer value that will be converted to pixels
		:param values: a pair of values representing the lower and upper bound
		:param min: the minimum value
		:param max: the maximum value
		:param step: the size of steps between positions on the slider
		:param orientation: either 'horizontal' or 'vertical'
		:param animate: if True, or if a numeric value in milliseconds specifying the animation length, this will cause the slider to animate when the user clicks to position it directly
		:param disabled: if True, causes the slider to appear disabled
		:return: the slider control
		"""

		self.__release_fn = release_fn
		self.__slide_fn = slide_fn
		self.__channel = MessageChannel()

		self.__width = '{0}px'.format(width) if isinstance(width, int) or isinstance(width, long)   else width

		options = {}
		if values is not None:
			options['values'] = values
		options['range'] = True
		if min is not None:
			options['min'] = min
		if max is not None:
			options['max'] = max
		if step is not None:
			options['step'] = step
		if orientation is not None:
			options['orientation'] = orientation
		if animate is not False:
			options['animate'] = animate
		if disabled:
			options['disabled'] = True
		self.__options = options


	def __on_change(self, event_name, ev_data):
		if self.__release_fn is not None:
			self.__release_fn(ev_data)

	def __on_slide(self, event_name, ev_data):
		self.__slide_fn(ev_data)


	def pres(self, pres_ctx):
		if self.__width is None:
			div = Html('<div></div>')
		else:
			div = Html('<div style="width: {0};"></div>'.format(self.__width))
		div = div.js_function_call('larch.controls.initRangeSlider', self.__slide_fn is not None, self.__options, self.__channel)
		div = div.with_event_handler("slider_change", self.__on_change)
		if self.__slide_fn is not None:
			div = div.with_event_handler("slider_slide", self.__on_slide)
		div = div.use_js('/static/larch_ui.js').use_css('/static/larch_ui.css')
		return div



class live_slider (CompositePres):
	def __init__(self, live, update_on_slide=False, width=None, min=None, max=None, step=None, orientation=None, animate=False,
		disabled=False):
		"""
		Create a JQuery UI slider that edits a live value

		:param live: the live value to edit
		:param update_on_slide: if True, the live value is updated in response to the user dragging, otherwise it only updates when the user lets the slider go
		:param width: the width of the slider, specified as a CSS value e.g. 200px (200 pixels) or 50%, or as an integer value that will be converted to pixels
		:param min: the minimum value
		:param max: the maximum value
		:param step: the size of steps between positions on the slider
		:param orientation: either 'horizontal' or 'vertical'
		:param animate: if True, or if a numeric value in milliseconds specifying the animation length, this will cause the slider to animate when the user clicks to position it directly
		:param disabled: if True, causes the slider to appear disabled
		:return: the slider control
		"""
		self.__live = live
		self.__update_on_slide = update_on_slide
		self.__width = width
		self.__min = min
		self.__max = max
		self.__step = step
		self.__orientation = orientation
		self.__animate = animate
		self.__disabled = disabled


	def __on_slide(self, value):
		self.__live.value = value


	def pres(self, pres_ctx):
		slide_fn = self.__on_slide if self.__update_on_slide   else None
		s = slider(self.__on_slide, slide_fn, self.__width, value=self.__live.static_value, min=self.__min, max=self.__max, step=self.__step,
			      orientation=self.__orientation, animate=self.__animate, disabled=self.__disabled)
		return s


def live_range_slider(live, update_on_slide=False, width=None, min=None, max=None, step=None, orientation=None,
		      animate=False, disabled=False):
	"""
	Create a JQuery UI range slider that edits a live value

	:param live: the live value to edit
	:param update_on_slide: if True, the live value is updated in response to the user dragging, otherwise it only updates when the user lets the slider go
	:param width: the width of the slider, specified as a CSS value e.g. 200px (200 pixels) or 50%, or as an integer value that will be converted to pixels
	:param min: the minimum value
	:param max: the maximum value
	:param step: the size of steps between positions on the slider
	:param orientation: either 'horizontal' or 'vertical'
	:param animate: if True, or if a numeric value in milliseconds specifying the animation length, this will cause the slider to animate when the user clicks to position it directly
	:param disabled: if True, causes the slider to appear disabled
	:return: the slider control
	"""

	def on_slide(value):
		live.value = value

	slide_fn = on_slide if update_on_slide   else None
	return range_slider(on_slide, slide_fn, width, values=live.static_value, min=min, max=max, step=step,
			    orientation=orientation, animate=animate, disabled=disabled)
