##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html
from larch.pres.pres import CompositePres
from larch.pres.resource import MessageChannel




class text_entry (CompositePres):
	def __init__(self, text, immediate_events=False, on_edit=None, size=None, width=None):
		"""
		Create a text entry control
		:param text: the initial text to display in the control
		:param immediate_events: if True, an event will be emitted each time the text is edited (on each keypress)
		:param on_edit: a callback invoked in response to edits, of the form function(modified_text)
		:param size: size of control in characters
		:param width: width, controlled by CSS
		:return: the editor control
		"""
		self.__text = text
		self.__immediate_events = immediate_events
		self.__on_edit = on_edit
		self.__size = size
		self.__width = width

		self.__channel = MessageChannel()


	def set_text(self, text):
		self.__channel.send(text)


	def pres(self, pres_ctx):
		sz = ''
		if self.__size is not None:
			sz += ' size="{0}"'.format(self.__size)
		if self.__width is not None:
			sz += ' style="width: {0};"'.format(self.__width)
		p = Html('<input type="text" value="{0}"{1}></input>'.format(self.__text, sz)).js_function_call('larch.controls.initTextEntry', self.__immediate_events, self.__channel)
		if self.__on_edit is not None:
			p = p.with_event_handler('text_entry_edit', lambda event_name, ev_data: self.__on_edit(ev_data))
		p = p.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
		return p




class live_text_entry (CompositePres):
	def __init__(self, live, immediate_events=False, size=None, width=None):
		"""
		Text entry control that edits a live value

		:param live: live value object whose value is to be edited
		:param immediate_events: if True, an event will be emitted each time the text is edited (on each keypress)
		:param size: size of control in characters
		:param width: width, controlled by CSS
		:return: the editor control
		"""
		self.__live = live
		self.__immediate_events = immediate_events
		self.__size = size
		self.__width = width


	def pres(self, pres_ctx):
		refreshing = [False]

		def set_value():
			s.set_text(self.__live.value)

		def on_change(incr):
			if not refreshing[0]:
				pres_ctx.fragment_view.queue_task(set_value)

		def __on_edit(value):
			refreshing[0] = True
			self.__live.value = value
			refreshing[0] = False

		self.__live.add_listener(on_change)

		s = text_entry(self.__live.static_value, self.__immediate_events, __on_edit, self.__size, self.__width)
		return s

