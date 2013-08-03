##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html


def ckeditor(text, immediate_events=False, config=None, on_edit=None, on_focus=None, on_blur=None):
	"""
	Create a ckEditor based rich text editor control
	:param text: The text to display in the editor
	:param immediate_events: If true, an event is emitted on each edit (key press)
	:param config: configuration options; see ckEditor documentation
	:param on_edit: a callback invoked in response to edits, of the form function(modified_html_text)
	:param on_focus: a callback invoked when the editor receives focus; of the form function()
	:param on_blur: a callback invoked when the editor loses focus; of the form function()
	:return: the ckEditor control
	"""
	if text == '':
		text = '<p></p>'
	if config is None:
		config = {}
	p = Html(u'<div contenteditable="true">{text}</div>'.format(text=text)).js_function_call('larch.controls.initCKEditor', config, immediate_events)
	p = p.use_js('/static/ckeditor/ckeditor.js')
	p = p.use_js('/static/larch_ui.js').use_css('/static/larch_ui.css')
	if on_edit is not None:
		p = p.with_event_handler('ckeditor_edit', lambda event_name, ev_data: on_edit(ev_data))
	if on_focus is not None:
		p = p.with_event_handler('ckeditor_focus', lambda event_name, ev_data: on_focus())
	if on_blur is not None:
		p = p.with_event_handler('ckeditor_blur', lambda event_name, ev_data: on_blur())
	return p
