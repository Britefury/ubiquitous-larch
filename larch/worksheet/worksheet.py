##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import _ast
import sys
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.pres.html import Html
from britefury.pres.key_event import Key
from larch.python import PythonCode


__author__ = 'Geoff'


class WorksheetBlock (object):
	def __init__(self, code=None):
		if code is None:
			code = PythonCode()
		else:
			assert isinstance(code, PythonCode)
		self.__code = code
		self.__result = None
		self.__incr = IncrementalValueMonitor()


	def execute(self, module):
		self.__result = self.__code.execute_in_module(module)
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()
		res = ['<div>', self.__result, '</div>']   if self.__result is not None  else []
		return Html(*(['<div class="python_console_block">', self.__code] + res + ['</div>']))




class Worksheet (object):
	def __init__(self, code=''):
		self.__blocks = [WorksheetBlock()]
		self.__incr = IncrementalValueMonitor()
		self._module = None


	def execute(self):
		self._module = imp.new_module('<Worksheet>')
		for block in self.__blocks:
			block.execute(self._module)



	def __present__(self, fragment):
		def on_execute():
			self.execute()

		def on_execute_key(key):
			self.execute()
			return True


		self.__incr.on_access()

		contents = []
		for block in self.__blocks:
			contents.extend(['<div>', block, '</div>'])

		p = Html(*contents)
		p = p.with_key_handler([Key(Key.KEY_DOWN, 13, ctrl=True)], on_execute_key)
		return p

