##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html

__code_mirror_theme = None

def set_code_mirror_theme(theme):
	global __code_mirror_theme
	__code_mirror_theme = theme

__addon_js = [
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

__addon_css = [
	'dialog/dialog.css',
	'hint/show-hint.css',
	'lint/lint.css',
	'merge/merge.css',
]

def code_mirror(text, immediate_events=False, config=None, on_edit=None, on_focus=None, on_blur=None, modes=None):
	if config is None:
		config = {}
	if modes is None:
		modes = []
	textarea = Html(u'<textarea>{text}</textarea>'.format(text=text))
	textarea = textarea.js_function_call('larch.controls.initCodeMirror', config, immediate_events)
	p = Html('<div>', textarea, '</div>')
	p = p.use_css('/static/codemirror-3.14/lib/codemirror.css')
	p = p.use_js('/static/codemirror-3.14/lib/codemirror.js')
	for mode in modes:
		p = p.use_js('/static/codemirror-3.14/mode/{0}/{0}.js'.format(mode))
	for addon in __addon_js:
		p = p.use_js('/static/codemirror-3.14/addon/{0}'.format(addon))
	for addon in __addon_css:
		p = p.use_css('/static/codemirror-3.14/addon/{0}'.format(addon))
	if __code_mirror_theme is not None:
		p = p.use_css('/static/codemirror-3.14/theme/{0}.css'.format(__code_mirror_theme))
	p = p.use_js('/static/bridge_codemirror.js')
	if on_edit is not None:
		p = p.with_event_handler('code_mirror_edit', lambda event_name, ev_data: on_edit(ev_data))
	if on_focus is not None:
		p = p.with_event_handler('code_mirror_focus', lambda event_name, ev_data: on_focus())
	if on_blur is not None:
		p = p.with_event_handler('code_mirror_blur', lambda event_name, ev_data: on_blur())
	return p
  