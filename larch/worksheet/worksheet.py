##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import _ast
import sys
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.pres.html import Html
from larch.python import PythonCode


__author__ = 'Geoff'


class WorksheetBlock (object):
	def __init__(self, code):
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
		self.__blocks = []
		self.__incr = IncrementalValueMonitor()
		self._module = imp.new_module('<Console>')



	def __present__(self, fragment):
		self.__incr.on_access()

		contents = []
		for block in self.__blocks:
			contents.extend(['<div>', block, '</div>'])

		return Html(*contents)

