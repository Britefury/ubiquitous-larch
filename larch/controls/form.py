##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.event_handler import EventHandler
from larch.pres.html import Html
from larch.pres.pres import CompositePres


class form (CompositePres):
	def __init__(self, contents, on_submit=None):
		"""
		Wrap the contents in a form that will be sent to Larch

		:param contents: The contents of the form, including the enclosing <form> tag
		:param on_submit: A callback invoked when the form is submitted. Callback signature: function(event); the form data is accessible through event.data
		:return: the form control
		"""
		self.__contents = contents
		self.submit = EventHandler()
		if on_submit is not None:
			self.submit.connect(on_submit)


	def pres(self, pres_ctx):
		p = Html('<form enctype="multipart/form-data">', self.__contents, '</form>').js_function_call('larch.controls.initForm').with_event_handler('form_submit', self.submit)
		p = p.use_js('/static/jquery/js/jquery.form.min.js').use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
		return p



def submit_button(text):
	"""
	Create a submit button with the given text

	:param text: The text contained in the button
	:return: the control
	"""
	return Html('<input type="submit" value="{0}"/>'.format(text)).js_eval('$(node).button();')