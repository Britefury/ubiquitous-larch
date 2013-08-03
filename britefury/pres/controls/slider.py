##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def slider(release_fn=None, slide_fn=None, width=None, value=None, min=None, max=None, step=None, orientation=None, animate=False, disabled=False):
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
	def on_change(event_name, ev_data):
		if release_fn is not None:
			release_fn(ev_data)

	def on_slide(event_name, ev_data):
		slide_fn(ev_data)

	width = '{0}px'.format(width)   if isinstance(width, int) or isinstance(width, long)   else width

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

	if width is None:
		div = Html('<div></div>')
	else:
		div = Html('<div style="width: {0};"></div>'.format(width))
	div = div.js_function_call('larch.controls.initSlider', slide_fn is not None, options)
	div = div.with_event_handler("slider_change", on_change)
	if slide_fn is not None:
		div = div.with_event_handler("slider_slide", on_slide)
	div = div.use_js('/static/larch_ui.js').use_css('/static/larch_ui.css')
	return div



def range_slider(release_fn=None, slide_fn=None, width=None, values=None, min=None, max=None, step=None, orientation=None, animate=False, disabled=False):
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
	def on_change(event_name, ev_data):
		if release_fn is not None:
			release_fn(ev_data)

	def on_slide(event_name, ev_data):
		slide_fn(ev_data)

	width = '{0}px'.format(width)   if isinstance(width, int) or isinstance(width, long)   else width

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

	if width is None:
		div = Html('<div></div>')
	else:
		div = Html('<div style="width: {0};"></div>'.format(width))
	div = div.js_function_call('larch.controls.initRangeSlider', slide_fn is not None, options)
	div = div.with_event_handler("slider_change", on_change)
	if slide_fn is not None:
		div = div.with_event_handler("slider_slide", on_slide)
	div = div.use_js('/static/larch_ui.js').use_css('/static/larch_ui.css')
	return div



def live_slider(live, update_on_slide=False, width=None, min=None, max=None, step=None, orientation=None, animate=False, disabled=False):
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
	def on_slide(value):
		live.value = value

	slide_fn = on_slide   if update_on_slide   else None
	return slider(on_slide, slide_fn, width, value=live.static_value, min=min, max=max, step=step, orientation=orientation, animate=animate, disabled=disabled)


def live_range_slider(live, update_on_slide=False, width=None, min=None, max=None, step=None, orientation=None, animate=False, disabled=False):
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

	slide_fn = on_slide   if update_on_slide   else None
	return range_slider(on_slide, slide_fn, width, values=live.static_value, min=min, max=max, step=step, orientation=orientation, animate=animate, disabled=disabled)
