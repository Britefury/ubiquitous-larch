##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.event_handler import EventHandler
from larch.pres.html import Html
from larch.pres.pres import CompositePres
from larch.pres.resource import MessageChannel

_code_mirror_theme = None

def set_code_mirror_theme(theme):
	"""
	Set the global code mirror theme

	:param theme: the name of the theme
	:return: None
	"""
	global _code_mirror_theme
	_code_mirror_theme = theme

_addon_js = [
	'comment/comment.js',
	'dialog/dialog.js',
	'display/placeholder.js',
	'edit/closebrackets.js',
	'edit/closetag.js',
	'edit/continuecomment.js',
	'edit/continuelist.js',
	'edit/matchbrackets.js',
	'edit/trailingspace.js',
	'fold/brace-fold.js',
	'fold/foldcode.js',
	'fold/indent-fold.js',
	'fold/xml-fold.js',
	'hint/html-hint.js',
	'hint/javascript-hint.js',
	'hint/pig-hint.js',
	'hint/python-hint.js',
	'hint/show-hint.js',
	'hint/xml-hint.js',
	'lint/coffeescript-lint.js',
	'lint/javascript-lint.js',
	'lint/json-lint.js',
	'lint/lint.js',
	'merge/dep/diff_match_patch.js',
	'merge/merge.js',
	'mode/loadmode.js',
	'mode/multiplex.js',
	'mode/overlay.js',
	'search/match-highlighter.js',
	'search/search.js',
	'search/searchcursor.js',
	'selection/active-line.js',
	'selection/mark-selection.js',
]

_addon_css = [
	'dialog/dialog.css',
	'hint/show-hint.css',
	'lint/lint.css',
	'merge/merge.css',
]


class code_mirror (CompositePres):
	def __init__(self, text, immediate_events=False, config=None, on_edit=None, on_focus=None, on_blur=None, modes=None):
		"""
		Create a CodeMirror based code editor control
		:param text: the initial text to display in the control
		:param immediate_events: if True, an event will be emitted each time the text is edited (on each keypress)
		:param config: configuration options (see CodeMirror documentation)
		:param on_edit: a callback invoked in response to edits, of the form function(event, modified_text)
		:param on_focus: a callback invoked when the editor receives focus; of the form function(event)
		:param on_blur: a callback invoked when the editor loses focus; of the form function(event)
		:param modes: a list of names of language plugins to load (e.g. 'python', 'javascript', 'glsl', etc; see CodeMirror documentation)
		:return: the editor control
		"""
		if config is None:
			config = {}
		if modes is None:
			modes = []

		self.__text = text
		self.__immediate_events = immediate_events
		self.__config = config
		self.edit = EventHandler()
		self.focus = EventHandler()
		self.blur = EventHandler()
		if on_edit is not None:
			self.edit.connect(on_edit)
		if on_focus is not None:
			self.focus.connect(on_focus)
		if on_blur is not None:
			self.blur.connect(on_blur)
		self.__modes = modes

		self.__channel = MessageChannel()


	def set_text(self, text):
		self.__channel.send(text)


	def pres(self, pres_ctx):
		textarea = Html(u'<textarea>{text}</textarea>'.format(text=Html.escape_str(self.__text)))
		textarea = textarea.js_function_call('larch.controls.initCodeMirror', self.__config, self.__immediate_events, self.__channel)
		p = Html('<div>', textarea, '</div>')
		p = p.use_css('/static/codemirror-3.14/lib/codemirror.css')
		p = p.use_js('/static/codemirror-3.14/lib/codemirror.js')
		for mode in self.__modes:
			p = p.use_js('/static/codemirror-3.14/mode/{0}/{0}.js'.format(mode))
		for addon in _addon_js:
			p = p.use_js('/static/codemirror-3.14/addon/{0}'.format(addon))
		for addon in _addon_css:
			p = p.use_css('/static/codemirror-3.14/addon/{0}'.format(addon))
		if _code_mirror_theme is not None:
			p = p.use_css('/static/codemirror-3.14/theme/{0}.css'.format(_code_mirror_theme))
		p = p.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
		p = p.with_event_handler('code_mirror_edit', lambda event: self.edit(event, event.data))
		p = p.with_event_handler('code_mirror_focus', self.focus)
		p = p.with_event_handler('code_mirror_blur', self.blur)
		return p




class live_code_mirror (CompositePres):
	def __init__(self, live, immediate_events=False, config=None, on_focus=None, on_blur=None, modes=None, text_filter_fn=None):
		"""
		ckEditor that edits a live value

		:param live: live value object whose value is to be edited
		:param immediate_events: if True, an event will be emitted each time the text is edited (on each keypress)
		:param config: configuration options (see CodeMirror documentation)
		:param on_focus: a callback invoked when the editor receives focus; of the form function()
		:param on_blur: a callback invoked when the editor loses focus; of the form function()
		:param modes: a list of names of language plugins to load (e.g. 'python', 'javascript', 'glsl', etc; see CodeMirror documentation)
		:param text_filter_fn: a callable that is invoked to filter incoming text from the user before assigning it to the live value
		:return: the editor control
		"""
		self.__live = live
		self.__immediate_events = immediate_events
		self.__config = config
		self.__on_focus = on_focus
		self.__on_blur = on_blur
		self.__modes = modes
		self.__text_filter_fn = text_filter_fn


	def pres(self, pres_ctx):
		refreshing = [False]

		def set_value():
			s.set_text(self.__live.value)

		def on_change(incr):
			if not refreshing[0]:
				pres_ctx.fragment_view.queue_task(set_value)

		def __on_edit(event, value):
			refreshing[0] = True
			if self.__text_filter_fn is not None:
				value = self.__text_filter_fn(value)
			self.__live.value = value
			refreshing[0] = False


		self.__live.add_listener(on_change)

		s = code_mirror(self.__live.static_value, self.__immediate_events, self.__config, __on_edit, self.__on_focus, self.__on_blur, self.__modes)
		return s


