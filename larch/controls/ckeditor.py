##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.event_handler import EventHandler
from larch.pres.html import Html
from larch.pres.pres import CompositePres
from larch.pres.resource import MessageChannel


class ckeditor (CompositePres):
	def __init__(self, text, immediate_events=False, use_edit_button=False, config=None, on_edit=None, on_focus=None, on_blur=None):
		"""
		Create a ckEditor based rich text editor control
		:param text: The text to display in the editor
		:param immediate_events: If true, an event is emitted on each edit (key press)
		:param use_edit_button: If true, the user must click an edit button to make the text editable
		:param config: configuration options; see ckEditor documentation
		:param on_edit: a callback invoked in response to edits, of the form function(event, modified_html_text)
		:param on_focus: a callback invoked when the editor receives focus; of the form function(event)
		:param on_blur: a callback invoked when the editor loses focus; of the form function(event)
		:return: the ckEditor control
		"""
		if text == '':
			text = '<p></p>'
		if config is None:
			config = {}

		self.__text = text
		self.__config = config
		self.__immediate_events = immediate_events
		self.__use_edit_button = use_edit_button
		self.edit = EventHandler()
		self.focus = EventHandler()
		self.blur = EventHandler()
		if on_edit is not None:
			self.edit.connect(on_edit)
		if on_focus is not None:
			self.focus.connect(on_focus)
		if on_blur is not None:
			self.blur.connect(on_blur)

		self.__channel = MessageChannel()


	def set_text(self, text):
		self.__channel.send(text)


	def pres(self, pres_ctx):
		if self.__use_edit_button:
			p = Html(u'<div class="__larch_ui_ckeditor_edit_container"><div>{text}</div></div>'.format(text=self.__text)).js_function_call('larch.controls.initCKEditorWithEditButton', self.__config, self.__immediate_events, self.__channel)
		else:
			p = Html(u'<div contenteditable="true">{text}</div>'.format(text=self.__text))
			p = p.js_function_call('larch.controls.initCKEditor', self.__config, self.__immediate_events, self.__channel)
			p = p.js_shutdown_function_call('larch.controls.shutdownCKEditor')

		p = p.use_js('/static/ckeditor/ckeditor.js')
		p = p.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
		p = p.with_event_handler('ckeditor_edit', lambda event: self.edit(event, event.data))
		p = p.with_event_handler('ckeditor_focus', self.focus)
		p = p.with_event_handler('ckeditor_blur', self.blur)
		return p




class live_ckeditor (CompositePres):
	def __init__(self, live, immediate_events=False, use_edit_button=False, config=None, on_focus=None, on_blur=None):
		"""
		ckEditor that edits a live value

		:param live: live value object whose value is to be edited
		:param immediate_events: If true, an event is emitted on each edit (key press)
		:param use_edit_button: If true, the user must click an edit button to make the text editable
		:param config: configuration options; see ckEditor documentation
		:param on_focus: a callback invoked when the editor receives focus; of the form function(event)
		:param on_blur: a callback invoked when the editor loses focus; of the form function(event)
		:return: the ckEditor control
		"""
		self.__live = live
		self.__immediate_events = immediate_events
		self.__use_edit_button = use_edit_button
		self.__config = config
		self.__on_focus = on_focus
		self.__on_blur = on_blur


	def pres(self, pres_ctx):
		refreshing = [False]
		val = [self.__live.static_value]

		def set_value():
			val[0] = self.__live.value
			s.set_text(self.__live.value)

		def on_change(incr):
			if not refreshing[0]:
				pres_ctx.fragment_view.queue_task(set_value)

		def __on_edit(event, html):
			refreshing[0] = True
			# WORKAROUND WHILE ckEditor kills caret position in response to OTHER ckEditor instances being modified
			#self.__live.value = value
			val[0] = event.data
			refreshing[0] = False

		# WORKAROUND WHILE ckEditor kills caret position in response to OTHER ckEditor instances being modified
		def __on_blur(event):
			refreshing[0] = True
			self.__live.value = val[0]
			refreshing[0] = False
			if self.__on_blur is not None:
				self.__on_blur(event)


		self.__live.add_listener(on_change)

		s = ckeditor(self.__live.static_value, self.__immediate_events, self.__use_edit_button, self.__config, __on_edit, on_focus=self.__on_focus, on_blur=__on_blur)
		return s


