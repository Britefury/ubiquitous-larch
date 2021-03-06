##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
##-*************************
from larch.event_handler import EventHandler
from larch.pres.html import Html
from larch.pres.pres import CompositePres
from larch.pres.resource import MessageChannel


class spinner (CompositePres):
	def __init__(self, on_change=None, value=0, input_name='spinner'):
		"""
		jQuery UI spinner control

		:param on_change: callback that is invoked when the spinner's value changes; function(value)
		:param value: [optional] initial value
		:param input_name: [optional] name attribute for input tag
		"""
		self.change = EventHandler()

		self.__value = value
		self.__input_name = input_name
		self.__channel = MessageChannel()

		if on_change is not None:
			self.change.connect(on_change)



	def __on_spinner_change(self, event):
		self.change(event, event.data)


	def set_value(self, value):
		self.__channel.send(value)


	def pres(self, pres_ctx):
		spin = Html('<input name={0} value={1} />'.format(self.__input_name, self.__value))
		spin = spin.js_function_call('larch.controls.initSpinner', self.__channel)
		spin = spin.with_event_handler("spinner_change", self.__on_spinner_change)
		spin = spin.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
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

		def on_live_change(incr):
			if not refreshing[0]:
				pres_ctx.fragment_view.queue_task(set_value)

		def __on_spin(event, value):
			refreshing[0] = True
			self.__live.value = value
			refreshing[0] = False

		self.__live.add_listener(on_live_change)

		s = spinner(__on_spin, value=self.__live.static_value, input_name=self.__name)
		return s



