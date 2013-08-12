##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html
from larch.pres.pres import CompositePres
from larch.pres.resource import MessageChannel


class spinner (CompositePres):
	def __init__(self, action_fn=None, value=0, name='spinner'):
		"""
		jQuery UI spinner control

		:param action_fn: callback that is invoked when the spinner's value changes; function(value)
		:param value: [optional] initial value
		:param name: [option] name attribute for input tag
		"""
		self.__action_fn = action_fn
		self.__value = value
		self.__name = name
		self.__channel = MessageChannel()



	def __on_spinner_change(self, event_name, ev_data):
		self.__action_fn(ev_data)


	def set_value(self, value):
		self.__channel.send(value)


	def pres(self, pres_ctx):
		spin = Html('<input name={0} value={1} />'.format(self.__name, self.__value))
		spin = spin.js_function_call('larch.controls.initSpinner', self.__channel)
		if self.__action_fn is not None:
			spin = spin.with_event_handler("spinner_change", self.__on_spinner_change)
		spin = spin.use_js('/static/larch_ui.js').use_css('/static/larch_ui.css')
		return spin



class live_spinner (CompositePres):
	def __init__(self, live, name='spinner'):
		"""
		jQuery UI spinner control that edits a live value

		:param live: live value object whose value is to be edited
		:param name: [option] name attribute for input tag
		"""
		self.__live = live
		self.__name = name


	def pres(self, pres_ctx):
		refreshing = [False]

		def set_value():
			s.set_value(self.__live.value)

		def on_change(incr):
			if not refreshing[0]:
				pres_ctx.fragment_view.queue_task(set_value)

		def __on_spin(value):
			refreshing[0] = True
			self.__live.value = value
			refreshing[0] = False

		self.__live.add_listener(on_change)

		s = spinner(__on_spin, value=self.__live.static_value, name=self.__name)
		return s



