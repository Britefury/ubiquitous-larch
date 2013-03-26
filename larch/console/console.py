##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import _ast
import sys
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.pres.html import Html
from britefury.pres.key_event import Key
from britefury.pres.controls import button
from britefury.projection.subject import Subject
from larch.python import PythonCode


__author__ = 'Geoff'




class ConsoleBlock (object):
	def __init__(self, code, result):
		assert isinstance(code, PythonCode)
		self.__code = code
		self.__result = result


	def __present__(self, fragment):
		res = ['<div>', self.__result, '</div>']   if self.__result is not None  else []
		return Html(*(['<div class="python_console_block">', self.__code] + res + ['</div>']))



class CurrentBlock (object):
	def __init__(self, code, console):
		self.__python_code = PythonCode(code)
		self.__console = console


	@property
	def python_code(self):
		return self.__python_code


	def __present__(self, fragment):
		def on_execute():
			self.__console._execute_current_block(self)

		def on_execute_key(key):
			on_execute()
			return True


		code_area = Html('<div>', self.__python_code, '</div>')
		execute_button = button.button('Execute', on_execute)

		code_area_with_key_handler = code_area.with_key_handler([Key(Key.KEY_DOWN, 13, ctrl=True)], on_execute_key)

		return Html('<div>', code_area_with_key_handler, execute_button, '</div>')





class Console (object):
	def __init__(self, code=''):
		self.__blocks = []
		self.__current_block = CurrentBlock(code, self)
		self.__incr = IncrementalValueMonitor()
		self._module = imp.new_module('<Console>')



	def _execute_current_block(self, block):
		result = block.python_code.execute_in_module(self._module)

		block.python_code.editable = False
		self.__blocks.append(ConsoleBlock(block.python_code, result))
		self.__current_block = CurrentBlock('', self)
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()

		preamble = sys.version + '\n' + 'Press Control+Enter to execute.'
		contents = ['<div class="python_console_header">{0}</div>'.format(preamble.replace('\n', '<br>'))]
		for block in self.__blocks + [self.__current_block]:
			contents.extend(['<div>', block, '</div>'])

		return Html(*contents).use_css('/console.css')


	def __subject__(self, enclosing_subject, perspective):
		return Subject(enclosing_subject, self, perspective, 'Python console')
