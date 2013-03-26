##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import _ast
import sys
from collections import namedtuple
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
			return Html('<div>', Pres.coerce_nullable(self.__result[0]), '</div>')




class ExecutionResultValue (object):
	def __init__(self, value):
		self.value = value


	def __present__(self, fragment):
		return Pres.coerce(self.value)



class ExecutionResultException (object):
	def __init__(self, exc_instance, trace_back):
		self.exc_instance = exc_instance
		self.trace_back = trace_back


	def __present__(self, fragment):
		return present_exception(self.exc_instance, self.trace_back)





class PythonCode (object):
	def __init__(self, code=None, editable=True):
		if code is None:
			code = ''
		self.__code = code
		self.__editable = editable
		self.__incr = IncrementalValueMonitor()
		self.on_focus = None
		self.on_blur = None


	def __getstate__(self):
		return {'code': self.__code, 'editable': self.__editable}

	def __setstate__(self, state):
		self.__code = state.get('code', '')
		self.__editable = state.get('editable', True)
		self.__incr = IncrementalValueMonitor()
		self.on_focus = None
		self.on_blur = None



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





	def execute_in_module(self, module):
		return self.execute(module.__name__, module.__dict__)



	def execute(self, module_name, env):
		ast_module = compile(self.code, module_name, 'exec', flags=_ast.PyCF_ONLY_AST)

		exec_code = None
		eval_code = None
		if len(ast_module.body) > 0:
			last_statement = ast_module.body[-1]
			if isinstance(last_statement, _ast.Expr):
				# The last statement is an expression
				expr = last_statement.value

				exec_code = compile(_ast.Module(body=ast_module.body[:-1]), module_name, 'exec')
				eval_code = compile(_ast.Expression(body=expr), module_name, 'eval')
			else:
				exec_code = compile(ast_module, module_name, 'exec')


		env = env

		try:
			if exec_code is not None:
				exec exec_code in env
			if eval_code is not None:
				return ExecutionResultValue(eval(eval_code, env))
			else:
				return None
		except Exception, e:
			return ExecutionResultException(e, sys.exc_info()[2])






	def __present__(self, fragment):
		self.__incr.on_access()

		def on_change(ev_data):
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



		code_area = code_mirror.code_mirror(self.__code, config=config, on_edit=on_change, on_focus=self.on_focus, on_blur=self.on_blur)
		code_area = code_area.use_js('/codemirror/mode/python/python.js')


		return Html('<div>', code_area, '</div>')

