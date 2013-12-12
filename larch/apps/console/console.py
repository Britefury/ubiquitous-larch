##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import sys
from larch import larch_builtins
from larch.incremental import IncrementalValueMonitor
from larch.pres.html import Html
from larch.pres.key_event import KeyAction
from larch.core.subject import Subject
from larch.apps.source_code import AbstractSourceCode, PythonCode
from larch.controls import button


__author__ = 'Geoff'




class ConsoleBlock (object):
	def __init__(self, code, result):
		assert isinstance(code, AbstractSourceCode)
		self.__code = code
		self.__result = result


	def __present__(self, fragment):
		res = ['<div>', self.__result, '</div>']   if self.__result is not None  else []
		return Html(*(['<div class="python_console_block">', self.__code] + res + ['</div>']))



class CurrentBlock (object):
	def __init__(self, code, console):
		assert isinstance(code, AbstractSourceCode)
		self.__code = code
		self.__console = console


	@property
	def code(self):
		return self.__code


	def __present__(self, fragment):
		def on_execute(event):
			self.__console._execute_current_block(self)

		def on_execute_key(event, key):
			on_execute(event)
			return True


		code_area = Html('<div>', self.__code, '</div>')
		execute_button = button.button('Execute', on_execute)

		code_area_with_key_handler = code_area.with_key_handler([KeyAction(KeyAction.KEY_DOWN, 13, ctrl=True)], on_execute_key)

		return Html('<div>', code_area_with_key_handler, execute_button, '</div>')





class AbstractConsole (object):
	def __init__(self, code=''):
		self.__blocks = []
		self.__current_block = CurrentBlock(self._source_text_to_code_object(code), self)
		self.__incr = IncrementalValueMonitor()



	def _execute_current_block(self, block):
		result = self._get_result_of_executing_code(block.code)

		block.code.editable = False
		self.__blocks.append(ConsoleBlock(block.code, result))
		self.__current_block = CurrentBlock(self._source_text_to_code_object(''), self)
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()

		preamble = self._get_console_preamble_text() + '\n' + 'Press Control+Enter to execute.'
		contents = ['<div class="python_console_header">{0}</div>'.format(preamble.replace('\n', '<br>'))]
		for block in self.__blocks + [self.__current_block]:
			contents.extend(['<div>', block, '</div>'])

		return Html(*contents).use_css('/static/larch/console.css')



	def _source_text_to_code_object(self, source_text):
		raise NotImplementedError, 'abstract'

	def _get_result_of_executing_code(self, code):
		raise NotImplementedError, 'abstract'

	def _get_console_preamble_text(self):
		raise NotImplementedError, 'abstract'




class PythonConsole (AbstractConsole):
	def __init__(self, code=''):
		super(PythonConsole, self).__init__(code)
		self._module = imp.new_module('<Console>')
		larch_builtins.init_module(self._module)


	def add_global(self, name, value):
		setattr(self._module, name, value)


	def _source_text_to_code_object(self, source_text):
		return PythonCode(source_text)

	def _get_result_of_executing_code(self, code):
		return code.execute_in_module(self._module)


	def _get_console_preamble_text(self):
		return sys.version


	def __subject__(self, enclosing_subject, location_trail, perspective):
		return Subject(enclosing_subject, location_trail, self, perspective, 'Python console')

