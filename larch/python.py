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


TextBlockStyle = namedtuple('TextBlockStyle', ['block_style', 'name_style', 'content_style'])


class TextOutBlock (object):
	def __init__(self, name, style):
		self.name = name
		self.content = ''
		self.style = style


	def write(self, text):
		self.content += text


	def __present__(self, fragment):
		return Html('<div class="{0}"><p class="{1}">{2}</p><pre class="{3}">{4}</pre></div>'.format(self.style.block_style, self.style.name_style, self.name, self.style.content_style, self.content))





class InterleavedTextOutStream (object):
	class _NamedStream (object):
		def __init__(self, interleaved_stream, name):
			self.interleaved_stream = interleaved_stream
			self.name = name


		def write(self, text):
			self.interleaved_stream.write(self.name, text)


	def __init__(self, style_map):
		self.blocks = []
		self.style_map = style_map


	def named_stream(self, name):
		return self._NamedStream(self, name)


	def is_empty(self):
		return len(self.blocks) > 0


	@property
	def current_block(self):
		return self.blocks[-1]   if len(self.blocks) > 0   else None


	def write(self, block_name, text):
		current = self.current_block
		change = current is None  or  current.name != block_name
		if change:
			self.blocks.append(TextOutBlock(block_name, self.style_map[block_name]))
		self.current_block.write(text)


	def __present__(self, fragment):
		return Html(*self.blocks)





class ExecutionResultEmpty (object):
	def __init__(self, streams):
		self.streams = streams


	def __present__(self, fragment):
		return Pres.coerce(self.streams)



class ExecutionResultValue (ExecutionResultEmpty):
	def __init__(self, streams, value):
		super(ExecutionResultValue, self).__init__(streams)
		self.value = value


	def __present__(self, fragment):
		return Html(self.streams, Pres.coerce_nullable(self.value))



class ExecutionResultException (ExecutionResultEmpty):
	def __init__(self, streams, exc_instance, trace_back):
		super(ExecutionResultException, self).__init__(streams)
		self.exc_instance = exc_instance
		self.trace_back = trace_back


	def __present__(self, fragment):
		return Html(self.streams, present_exception(self.exc_instance, self.trace_back))





_stream_style_map = {
	'stdout': TextBlockStyle('python_stdout_block', 'python_stdout_name', 'python_stdout_text'),
	'stderr': TextBlockStyle('python_stderr_block', 'python_stderr_name', 'python_stderr_text')
}


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
		streams = InterleavedTextOutStream(_stream_style_map)
		old_out, old_err = sys.stdout, sys.stderr
		sys.stdout = streams.named_stream('stdout')
		sys.stderr = streams.named_stream('stderr')

		try:

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

			if exec_code is not None:
				exec exec_code in env
			if eval_code is not None:
				val = eval(eval_code, env)
				return ExecutionResultValue(streams, val)
			else:
				return ExecutionResultEmpty(streams)
		except Exception, e:
			return ExecutionResultException(streams, e, sys.exc_info()[2])
		finally:
			sys.stdout, sys.stdin = old_out, old_err






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

