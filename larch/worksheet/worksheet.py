##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import sys

from britefury.incremental import IncrementalValueMonitor
from britefury.pres.html import Html
from britefury.pres.key_event import KeyAction
from britefury.pres.controls import ckeditor, menu, button, text_entry
from britefury.projection.subject import Subject
from britefury.live.live_value import LiveValue
from britefury import command
from larch import source_code


__author__ = 'Geoff'


class WorksheetBlock (object):
	def __init__(self, worksheet):
		self._worksheet = worksheet


	def __getstate__(self):
		return {'worksheet': self._worksheet}

	def __setstate__(self, state):
		self._worksheet = state.get('worksheet')


	def _on_focus(self):
		self._worksheet._notify_focus(self)


	def execute(self, module):
		pass



class WorksheetBlockText (WorksheetBlock):
	def __init__(self, worksheet, text=None):
		super(WorksheetBlockText, self).__init__(worksheet)
		if text is None:
			text = ''
		self.__text = text
		self.__incr = IncrementalValueMonitor()


	def __getstate__(self):
		state = super(WorksheetBlockText, self).__getstate__()
		state['text'] = self.__text
		return state

	def __setstate__(self, state):
		super(WorksheetBlockText, self).__setstate__(state)
		self.__text = state.get('text', '')
		self.__incr = IncrementalValueMonitor()



	def __present__(self, fragment):
		self.__incr.on_access()

		def on_edit(text):
			self.__text = text
			self.__incr.on_changed()

		p = ckeditor.ckeditor(self.__text, on_edit=on_edit, on_focus=self._on_focus)

		return Html('<div class="worksheet_block">', p, '</div>')



class WorksheetBlockCode (WorksheetBlock):
	def __init__(self, worksheet):
		super(WorksheetBlockCode, self).__init__(worksheet)
		self.__code = source_code.PythonCode()
		self.__code.on_focus = self._on_focus
		self.__result = None
		self.__incr = IncrementalValueMonitor()


	def __getstate__(self):
		state = super(WorksheetBlockCode, self).__getstate__()
		state['code'] = self.__code
		return state

	def __setstate__(self, state):
		super(WorksheetBlockCode, self).__setstate__(state)
		self.__code = state.get('code')
		if self.__code is None:
			self.__code = source_code.PythonCode()
		self.__code.on_focus = self._on_focus
		self.__result = None
		self.__incr = IncrementalValueMonitor()



	def execute(self, module):
		self.__result = self.__code.execute_in_module(module)
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()
		header = Html('<div class="worksheet_python_code_header">Python code (executable)</div>')
		code = Html('<div class="worksheet_python_code_container">', self.__code, '</div>')
		res = ['<div class="worksheet_result_container">', self.__result, '</div>']   if self.__result is not None  else []
		return Html(*(['<div class="worksheet_code_block">', header, '<div class="worksheet_code_block_body">', code] + res + ['</div></div>']))




class WorksheetBlockSource (WorksheetBlock):
	__language_to_type_map = {
		'html': source_code.HtmlCode,
		'css': source_code.CSSCode,
		'js': source_code.JSCode,
		'glsl': source_code.GLSLCode,
	}

	__type_to_language_map = {
		source_code.HtmlCode: 'html',
		source_code.CSSCode: 'css',
		source_code.JSCode: 'js',
		source_code.GLSLCode: 'glsl',
	}

	__language_to_human_name = {
		'html': 'HTML',
		'css': 'CSS',
		'js': 'Javascript',
		'glsl': 'GLSL',
	}

	def __init__(self, worksheet, language, var_name='src'):
		super(WorksheetBlockSource, self).__init__(worksheet)
		try:
			code_type = self.__language_to_type_map[language]
		except KeyError:
			raise ValueError, 'Invalid language {0}'.format(language)

		self.__code = code_type()
		self.__code.on_focus = self._on_focus
		self.__var_name = var_name
		self.__incr = IncrementalValueMonitor()


	def __getstate__(self):
		state = super(WorksheetBlockSource, self).__getstate__()
		state['code'] = self.__code
		state['var_name'] = self.__var_name
		return state

	def __setstate__(self, state):
		super(WorksheetBlockSource, self).__setstate__(state)
		self.__code = state.get('code')
		self.__code.on_focus = self._on_focus
		self.__var_name = state.get('var_name')
		self.__incr = IncrementalValueMonitor()


	@property
	def language(self):
		return self.__type_to_language_map[type(self.__code)]

	@language.setter
	def language(self, lang):
		try:
			code_type = self.__language_to_type_map[lang]
		except KeyError:
			raise ValueError, 'Invalid language {0}'.format(lang)
		src_text = self.__code.source_text
		self.__code = code_type(code=src_text)
		self.__incr.on_changed()



	def execute(self, module):
		module.__dict__[self.__var_name] = self.__code.source_text


	def __present__(self, fragment):
		self.__incr.on_access()

		def _on_change_varname(name):
			self.__var_name = name

		def _on_change_language(lang):
			self.language = lang

		language = self.language


		var_name = text_entry.text_entry(self.__var_name, _on_change_varname)


		js_item = menu.item('Javascript', lambda: _on_change_language('js'))
		css_item = menu.item('CSS', lambda: _on_change_language('css'))
		glsl_item = menu.item('GLSL', lambda: _on_change_language('glsl'))
		#html_item = menu.item('HTML', lambda: _on_change_language('html'))

		lang_menu = menu.sub_menu('Change language', [
			js_item,
			css_item,
			glsl_item,
			#html_item
		])
		lang_menu_button = menu.menu([lang_menu], drop_down=True)


		human_lang_name = self.__language_to_human_name[language]

		header = Html('<div class="worksheet_{0}_code_header">'.format(language),
			      '<table class="worksheet_src_language_select_table"><tr>',
			      '<td>{0}</td>'.format(human_lang_name),
			      '<td>', lang_menu_button, '</td>',
			      '</tr></table>',
			      '<table><tr>',
			      '<td>Variable name:</td>',
			      '<td>', var_name, '</td>',
			      '</tr></table>',
			      '</div>')
		code = Html('<div class="worksheet_{0}_code_container">'.format(language), self.__code, '</div>')
		return Html('<div class="worksheet_code_block">', header, '<div class="worksheet_code_block_body">', code, '</div></div>')




class Worksheet (object):
	def __init__(self, code=''):
		self.__blocks = [WorksheetBlockCode(self)]
		self.__incr = IncrementalValueMonitor()
		self._module = None
		self.__focus_block = None
		self.__execution_state = LiveValue()
		self.__exec_state_init()


	def __exec_state_init(self):
		self.__execution_state.value = Html('<div class="worksheet_exec_state_init">Worksheet not yet executed; place the caret within a code block and press Control-Enter to execute.</div>')

	def __exec_state_executed(self):
		self.__execution_state.value = Html('<div class="worksheet_exec_state_executed">Re-execute code with Control-Enter.</div>')


	def __getstate__(self):
		return {'blocks': self.__blocks}


	def __setstate__(self, state):
		self.__blocks = state.get('blocks')
		if self.__blocks is None:
			self.__blocks = []
		self.__incr = IncrementalValueMonitor()
		self._module = None
		self.__focus_block = None
		self.__execution_state = LiveValue()
		self.__exec_state_init()


	def execute(self):
		self._module = imp.new_module('<Worksheet>')
		self.__execute_in_module(self._module)
		self.__exec_state_executed()


	def __execute_in_module(self, module):
		for block in self.__blocks:
			block.execute(module)



	def _notify_focus(self, block):
		self.__focus_block = block


	def _insert_block(self, block_to_insert, below):
		index = len(self.__blocks)
		if self.__focus_block is not None  and  self.__focus_block in self.__blocks:
			index = self.__blocks.index(self.__focus_block)
			if below:
				index += 1
		self.__blocks.insert(index, block_to_insert)
		self.__incr.on_changed()

	def _delete_block(self):
		if self.__focus_block is not None  and  self.__focus_block in self.__blocks:
			self.__blocks.remove(self.__focus_block)
			self.__incr.on_changed()



	def __load_module__(self, document, fullname):
		try:
			return sys.modules[fullname]
		except KeyError:
			pass

		mod = document.new_module(fullname, self)

		self.__execute_in_module(mod)

		return mod


	def __commands__(self):
		return [
			command.Command([command.Key(ord('R'))], 'Insert rich text below', lambda page: self._insert_block(WorksheetBlockText(self), True)),
			command.Command([command.Key(ord('P'))], 'Insert Python code below', lambda page: self._insert_block(WorksheetBlockCode(self), True)),
			command.Command([command.Key(ord('J'))], 'Insert Javascript source below', lambda page: self._insert_block(WorksheetBlockSource(self, 'js', 'js'), True)),
			command.Command([command.Key(ord('C'))], 'Insert CSS source below', lambda page: self._insert_block(WorksheetBlockSource(self, 'css', 'css'), True)),
			command.Command([command.Key(ord('G'))], 'Insert GLSL source below', lambda page: self._insert_block(WorksheetBlockSource(self, 'glsl', 'glsl'), True)),

			command.Command([command.Key(ord('A')), command.Key(ord('R'))], 'Insert rich text below', lambda page: self._insert_block(WorksheetBlockText(self), False)),
			command.Command([command.Key(ord('A')), command.Key(ord('P'))], 'Insert Python code below', lambda page: self._insert_block(WorksheetBlockCode(self), False)),
			command.Command([command.Key(ord('A')), command.Key(ord('J'))], 'Insert Javascript source below', lambda page: self._insert_block(WorksheetBlockSource(self, 'js', 'js'), False)),
			command.Command([command.Key(ord('A')), command.Key(ord('C'))], 'Insert CSS source below', lambda page: self._insert_block(WorksheetBlockSource(self, 'css', 'css'), False)),
			command.Command([command.Key(ord('A')), command.Key(ord('G'))], 'Insert GLSL source below', lambda page: self._insert_block(WorksheetBlockSource(self, 'glsl', 'glsl'), False)),

			command.Command([command.Key(ord('X'))], 'Remove block', lambda page: self._delete_block()),
		]



	def __present__(self, fragment):
		def on_execute():
			self.execute()

		def on_execute_key(key):
			self.execute()
			return True

		def save():
			subject = fragment.subject
			try:
				save = subject.document.save
			except AttributeError:
				print 'WARNING: Could not save; method unavailable'
				raise
			else:
				return save()
			return None

		def on_save_key(key):
			save_name = save()
			fragment.page.page_js_function_call('noty', {'text': 'Saved <span class="emph">{0}</span>'.format(save_name), 'type': 'success', 'timeout': 2000, 'layout': 'bottomCenter'})



		self.__incr.on_access()



		def _insert_rich_text(below):
			self._insert_block(WorksheetBlockText(self), below)

		def _insert_code(below):
			self._insert_block(WorksheetBlockCode(self), below)

		def _insert_js(below):
			self._insert_block(WorksheetBlockSource(self, 'js', 'js'), below)

		def _insert_css(below):
			self._insert_block(WorksheetBlockSource(self, 'css', 'css'), below)

		def _insert_glsl(below):
			self._insert_block(WorksheetBlockSource(self, 'glsl', 'glsl'), below)

		def _insert_html(below):
			self._insert_block(WorksheetBlockSource(self, 'html', 'html'), below)


		save_button = button.button('Save (Ctrl-S)', save)


		insert_rich_text_above = menu.item('Insert rich text above', lambda: _insert_rich_text(False))
		insert_code_above = menu.item('Insert executable Python code above', lambda: _insert_code(False))
		insert_js_above = menu.item('Insert JS source above', lambda: _insert_js(False))
		insert_css_above = menu.item('Insert CSS source above', lambda: _insert_css(False))
		insert_glsl_above = menu.item('Insert GLSL source above', lambda: _insert_glsl(False))
		insert_html_above = menu.item('Insert HTML source above', lambda: _insert_html(False))

		insert_rich_text_below = menu.item('Insert rich text below', lambda: _insert_rich_text(True))
		insert_code_below = menu.item('Insert executable Python code below', lambda: _insert_code(True))
		insert_js_below = menu.item('Insert JS source below', lambda: _insert_js(True))
		insert_css_below = menu.item('Insert CSS source below', lambda: _insert_css(True))
		insert_glsl_below = menu.item('Insert GLSL source below', lambda: _insert_glsl(True))
		insert_html_below = menu.item('Insert HTML source below', lambda: _insert_html(True))

		remove_block = menu.item('Remove block', lambda: self._delete_block())
		edit_menu = menu.sub_menu('Edit', [
			insert_rich_text_above,
			insert_code_above,
			insert_js_above,
			insert_css_above,
			insert_glsl_above,
			insert_html_above,

			menu.item('--------', None),
			insert_rich_text_below,
			insert_code_below,
			insert_js_below,
			insert_css_below,
			insert_glsl_below,
			insert_html_below,
			menu.item('--------', None),
			remove_block])

		page_menu = menu.menu([edit_menu], drop_down=True)

		exec_button = button.button('Execute (Ctrl-Enter)', self.execute)

		doc = Html('<div class="worksheet_documentation">The blocks within a worksheet are editable; place the cursor within them to edit them. Save with Ctrl-S, execute code with Ctrl-Enter.' + \
			'The Edit menu contains options for adding and removing blocks.</div>')

		header = Html('<div class="worksheet_header">',
			      '<div class="worksheet_menu_bar">',
			      '<div class="worksheet_menu">', page_menu, '</div>',
			      '<div class="worksheet_buttons">', save_button, exec_button,'</div>',
			      '</div>',
			      self.__execution_state,
			      doc,
			      '</div>')

		contents = [header]

		for block in self.__blocks:
			contents.extend(['<div>', block, '</div>'])


		p = Html(*contents)
		p = p.with_key_handler([KeyAction(KeyAction.KEY_DOWN, 13, ctrl=True)], on_execute_key)
		p = p.with_key_handler([KeyAction(KeyAction.KEY_DOWN, ord('S'), ctrl=True, prevent_default=True)], on_save_key)
		return p.use_css('/static/worksheet.css')

