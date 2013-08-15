##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import _ast
import sys
import re
from collections import namedtuple

from larch.incremental import IncrementalValueMonitor
from larch.live import LiveValue

from larch.inspector.present_exception import present_exception_with_traceback
from larch.pres.html import Html
from larch.pres.pres import Pres
from larch.controls import code_mirror


class AbstractSourceCode (object):
	__codemirror_modes__ = []
	__codemirror_config__ = None

	def __init__(self, code=None, editable=True):
		if code is None:
			code = ''
		self.__code = LiveValue(code)
		self.__editable = editable
		self.__incr = IncrementalValueMonitor()
		self.on_focus = None
		self.on_blur = None
		if self.__codemirror_config__ is None:
			raise TypeError, 'Abstract: __codemirror_config__ not defined'


	def __getstate__(self):
		return {'code': self.__code.static_value, 'editable': self.__editable}

	def __setstate__(self, state):
		self.__code = LiveValue(state.get('code', ''))
		self.__editable = state.get('editable', True)
		self.__incr = IncrementalValueMonitor()
		self.on_focus = None
		self.on_blur = None
		if self.__codemirror_config__ is None:
			raise TypeError, 'Abstract: __codemirror_config__ not defined'



	@property
	def editable(self):
		return self.__editable

	@editable.setter
	def editable(self, e):
		self.__editable = e
		self.__incr.on_changed()


	@property
	def source_text(self):
		return self.__code.static_value



	def _filter_source_text(self, text):
		"""
		Filter te source text when we receive a change event from the CodeMirror widget

		Override this method in cases where you need to modify the incoming source before it is stored in this object

		:param text: The incoming text
		:return: The filtered text
		"""
		return text





	def __present__(self, fragment):
		if self.__codemirror_config__ is None:
			raise TypeError, 'Abstract: __codemirror_config__ not defined'

		self.__incr.on_access()

		config = {}
		config.update(self.__codemirror_config__)
		config['readOnly'] = 'nocursor'   if not self.__editable   else False
		config['autofocus'] = self.__editable


		code_area = code_mirror.live_code_mirror(self.__code, config=config, on_focus=self.on_focus, on_blur=self.on_blur, modes=self.__codemirror_modes__, text_filter_fn=self._filter_source_text)


		return Html('<div>', code_area, '</div>')








TextBlockStyle = namedtuple('TextBlockStyle', ['block_style', 'name_style', 'content_style'])


class TextOutBlock (object):
	def __init__(self, name, style):
		self.name = name
		self.content = ''
		self.style = style


	def write(self, text):
		self.content += text


	def __present__(self, fragment):
		escaped_content = Html.escape_str(self.content).replace('\n', '<br>')
		return Html('<div class="{0}"><p class="{1}">{2}</p><pre class="{3}">{4}</pre></div>'.format(self.style.block_style, self.style.name_style, self.name, self.style.content_style, escaped_content))





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
		return Html(self.streams, Pres.coerce(self.value))



class ExecutionResultException (ExecutionResultEmpty):
	def __init__(self, streams, exc_instance, exc_value, trace_back):
		super(ExecutionResultException, self).__init__(streams)
		self.exc_instance = exc_instance
		self.exc_value = exc_value
		self.trace_back = trace_back


	def __present__(self, fragment):
		return Html(self.streams, present_exception_with_traceback(self.exc_instance, self.exc_value, self.trace_back))





_stream_style_map = {
	'stdout': TextBlockStyle('python_stdout_block', 'python_stdout_name', 'python_stdout_text'),
	'stderr': TextBlockStyle('python_stderr_block', 'python_stderr_name', 'python_stderr_text')
}


class PythonCode (AbstractSourceCode):
	__whitespace = re.compile('[ \t]+')
	__spaces_per_indent = 4
	__indent_replacement = ' ' * __spaces_per_indent

	__codemirror_modes__ = ['python']
	__codemirror_config__ = {
			'mode': {
				'name': 'python',
				'version': 2,
				'singleLineStringErrors': False
			},
			'lineNumbers': True,
			'indentUnit': 4,
			'tabMode': "shift",
			'matchBrackets': True
	}


	def __filter_line(self, line):
		# Match leading whitespace
		m = self.__whitespace.match(line)
		# Match succeeded and line is not all whitespace
		if m is not None  and  m.end(0) < len(line):
			# Replace the tabs with spaces
			g = m.group(0)
			ws = g.replace('\t', self.__indent_replacement)
			return ws + line[len(g):]
		else:
			return line

	def _filter_source_text(self, text):
		"""
		Within leading whitespace, replace tabs with spaces

		Sometimes CodeMirror can return a combination of both which results in IndentationError when the code is passed to the interpreter for execution
		:param text: Incoming source text
		:return: Filtered text
		"""
		# Filter each line in turn
		lines = text.split('\n')
		lines = [self.__filter_line(line)   for line in lines]
		return '\n'.join(lines)


	def execute_in_module(self, module):
		return self.execute(module.__name__, module.__dict__)



	def execute(self, module_name, env):
		streams = InterleavedTextOutStream(_stream_style_map)
		old_out, old_err = sys.stdout, sys.stderr
		sys.stdout = streams.named_stream('stdout')
		sys.stderr = streams.named_stream('stderr')

		try:

			ast_module = compile(self.source_text, module_name, 'exec', flags=_ast.PyCF_ONLY_AST)

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
			return ExecutionResultException(streams, e, sys.exc_info()[1],  sys.exc_info()[2])
		finally:
			sys.stdout, sys.stderr = old_out, old_err




class HtmlCode (AbstractSourceCode):
	__codemirror_modes__ = ['xml', 'javascript', 'css', 'htmlmixed']
	__codemirror_config__ = {
		'mode' : {
				'name': 'htmlmixed',
				'scriptTypes': []
		},
		'lineNumbers': True,
		'indentUnit': 4,
		'matchBrackets': True
	}



class CSSCode (AbstractSourceCode):
	__codemirror_modes__ = ['css']
	__codemirror_config__ = {
		'mode' : {
				'name': 'css',
		},
		'lineNumbers': True,
		'indentUnit': 4,
		'matchBrackets': True
	}



class JSCode (AbstractSourceCode):
	__codemirror_modes__ = ['javascript']
	__codemirror_config__ = {
		'mode' : {
				'name': 'javascript',
		},
		'lineNumbers': True,
		'indentUnit': 4,
		'matchBrackets': True
	}



class GLSLCode (AbstractSourceCode):
	__codemirror_modes__ = ['glsl']
	__codemirror_config__ = {
		'mode' : {
				'name': 'glsl',
		},
		'lineNumbers': True,
		'indentUnit': 4,
		'matchBrackets': True
	}
