##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import _ast
import sys
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.inspector.present_exception import present_exception
from britefury.pres.html import Html
from britefury.pres.key_event import Key
from britefury.pres.pres import Pres
from britefury.pres.controls import code_mirror, button


__author__ = 'Geoff'


class CodeResult (object):
	def __init__(self):
		self.__result = None
		self.__incr = IncrementalValueMonitor()


	@property
	def result(self):
		return self.__result

	@result.setter
	def result(self, r):
		self.__result = r
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()
		if self.__result is None:
			return Html('<div></div>')
		else:
			return Html('<div>', Pres.coerce(self.__result[0]), '</div>')


class PythonCode (object):
	def __init__(self, code, editable=True):
		self.__code = code
		self.__editable = editable
		self.__incr = IncrementalValueMonitor()


	@property
	def editable(self):
		return self.__editable

	@editable.setter
	def editable(self, e):
		self.__editable = e
		self.__incr.on_changed()


	@property
	def code(self):
		return self.__code


	def __present__(self, fragment):
		self.__incr.on_access()

		def on_change(event_name, ev_data):
			self.__code = ev_data

		config = {
			'mode': {
				'name': "python",
				'version': 2,
			 	'singleLineStringErrors': False},
			'lineNumbers': True,
			'indentUnit': 4,
			'tabMode': "shift",
			'matchBrackets': True,
			'readOnly': 'nocursor'   if not self.__editable   else False,
			'autofocus': self.__editable
		}
		code_area = code_mirror.code_mirror(self.__code, config, on_change)


		return Html('<div>', code_area, '</div>')



class ConsoleBlock (object):
	def __init__(self, code, result):
		assert isinstance(code, PythonCode)
		self.__code = code
		self.__result = result


	def __present__(self, fragment):
		res = ['<div>', self.__result[0], '</div>']   if self.__result is not None  else []
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
		src = block.python_code.code
		ast_module = compile(src, self._module.__name__, 'exec', flags=_ast.PyCF_ONLY_AST)

		exec_code = None
		eval_code = None
		if len(ast_module.body) > 0:
			last_statement = ast_module.body[-1]
			if isinstance(last_statement, _ast.Expr):
				# The last statement is an expression
				expr = last_statement.value

				exec_code = compile(_ast.Module(body=ast_module.body[:-1]), self._module.__name__, 'exec')
				eval_code = compile(_ast.Expression(body=expr), self._module.__name__, 'eval')
			else:
				exec_code = compile(ast_module, self._module.__name__, 'exec')


		env = self._module.__dict__

		try:
			if exec_code is not None:
				exec exec_code in env
			result = [eval(eval_code, env)]   if eval_code is not None   else None
		except Exception, e:
			result = [present_exception(e, sys.exc_info()[2])]

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



		return Html(*contents)

