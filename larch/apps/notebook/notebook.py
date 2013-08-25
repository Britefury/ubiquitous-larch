##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import sys
from larch.apps import source_code

from larch.incremental import IncrementalValueMonitor
from larch import command
from larch.live import LiveValue
from larch.pres.html import Html
from larch.pres.key_event import KeyAction
from larch.controls import ckeditor, menu, text_entry, focusable
from larch.controls import button


__author__ = 'Geoff'


class NotebookBlock (object):
	def __init__(self, notebook):
		self._notebook = notebook


	def __getstate__(self):
		return {'notebook': self._notebook}

	def __setstate__(self, state):
		self._notebook = state.get('notebook', state.get('worksheet'))


	def execute(self, module):
		pass



class NotebookBlockText (NotebookBlock):
	def __init__(self, notebook, text=None):
		super(NotebookBlockText, self).__init__(notebook)
		if text is None:
			text = ''
		self.__text = LiveValue(text)


	def __getstate__(self):
		state = super(NotebookBlockText, self).__getstate__()
		state['text'] = self.__text.static_value
		return state

	def __setstate__(self, state):
		super(NotebookBlockText, self).__setstate__(state)
		self.__text = LiveValue(state.get('text', ''))



	def __present__(self, fragment):
		p = ckeditor.live_ckeditor(self.__text)

		p = Html('<div class="notebook_block notebook_richtext">', p, '</div>')
		p = focusable.focusable(p)
		return p



class NotebookBlockCode (NotebookBlock):
	def __init__(self, notebook, code=None):
		super(NotebookBlockCode, self).__init__(notebook)
		self.__code = source_code.PythonCode(code=code)
		self.__result = None
		self.__incr = IncrementalValueMonitor()


	def __getstate__(self):
		state = super(NotebookBlockCode, self).__getstate__()
		state['code'] = self.__code
		return state

	def __setstate__(self, state):
		super(NotebookBlockCode, self).__setstate__(state)
		self.__code = state.get('code')
		if self.__code is None:
			self.__code = source_code.PythonCode()
		self.__result = None
		self.__incr = IncrementalValueMonitor()



	def execute(self, module):
		self.__result = self.__code.execute_in_module(module)
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()
		header = Html('<div class="notebook_python_code_header">Python code (executable)</div>')
		code = Html('<div class="notebook_python_code_container notebook_code_container">', self.__code, '</div>')
		res = ['<div class="notebook_result_container">', self.__result, '</div>']   if self.__result is not None  else []
		p = Html(*(['<div class="notebook_code_block">', header, '<div class="notebook_code_block_body">', code] + res + ['</div></div>']))
		p = focusable.focusable(p)
		return p





class NotebookBlockSource (NotebookBlock):
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

	def __init__(self, notebook, language, var_name='src'):
		super(NotebookBlockSource, self).__init__(notebook)
		try:
			code_type = self.__language_to_type_map[language]
		except KeyError:
			raise ValueError, 'Invalid language {0}'.format(language)

		self.__code = code_type()
		self.__var_name = var_name
		self.__incr = IncrementalValueMonitor()


	def __getstate__(self):
		state = super(NotebookBlockSource, self).__getstate__()
		state['code'] = self.__code
		state['var_name'] = self.__var_name
		return state

	def __setstate__(self, state):
		super(NotebookBlockSource, self).__setstate__(state)
		self.__code = state.get('code')
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
		html_item = menu.item('HTML', lambda: _on_change_language('html'))

		lang_menu = menu.sub_menu('Change language', [
			js_item,
			css_item,
			glsl_item,
			html_item
		])
		lang_menu_button = menu.menu([lang_menu], drop_down=True)


		human_lang_name = self.__language_to_human_name[language]

		header = Html('<div class="notebook_{0}_code_header">'.format(language),
			      '<table class="notebook_src_language_select_table"><tr>',
			      '<td>{0}</td>'.format(human_lang_name),
			      '<td>', lang_menu_button, '</td>',
			      '</tr></table>',
			      '<table><tr>',
			      '<td>Variable name:</td>',
			      '<td>', var_name, '</td>',
			      '</tr></table>',
			      '</div>')
		code = Html('<div class="notebook_{0}_code_container notebook_code_container">'.format(language), self.__code, '</div>')
		p = Html('<div class="notebook_code_block">', header, '<div class="notebook_code_block_body">', code, '</div></div>')
		p = focusable.focusable(p)
		return p





class Notebook (object):
	def __init__(self, blocks=None):
		if blocks is None:
			blocks = [NotebookBlockCode(self)]
		self.__blocks = blocks
		self.__incr = IncrementalValueMonitor()
		self._module = None
		self.__execution_state = LiveValue()
		self.__exec_state_init()


	def __exec_state_init(self):
		self.__execution_state.value = Html('<span class="notebook_exec_state_init">CODE NOT EXECUTED</span>')

	def __exec_state_executed(self):
		self.__execution_state.value = Html('')


	def __getstate__(self):
		return {'blocks': self.__blocks}


	def __setstate__(self, state):
		self.__blocks = state.get('blocks')
		if self.__blocks is None:
			self.__blocks = []
		self.__incr = IncrementalValueMonitor()
		self._module = None
		self.__execution_state = LiveValue()
		self.__exec_state_init()



	def append(self, block):
		self.__blocks.append(block)
		self.__incr.on_changed()


	def execute(self):
		self._module = imp.new_module('<Notebook>')
		self.__execute_in_module(self._module)
		self.__exec_state_executed()


	def __execute_in_module(self, module):
		for block in self.__blocks:
			block.execute(module)



	def _insert_block(self, block_to_insert, below, focus_block):
		index = len(self.__blocks)
		if focus_block is not None  and  focus_block in self.__blocks:
			index = self.__blocks.index(focus_block)
			if below:
				index += 1
		self.__blocks.insert(index, block_to_insert)
		self.__incr.on_changed()

	def _delete_block(self, focus_block):
		if focus_block is not None  and  focus_block in self.__blocks:
			self.__blocks.remove(focus_block)
			self.__incr.on_changed()



	def __load_module__(self, document, fullname):
		try:
			return sys.modules[fullname]
		except KeyError:
			pass

		mod = document.new_module(fullname, self)

		self.__execute_in_module(mod)

		return mod



	def _save_containing_document(self, fragment):
		subject = fragment.subject
		try:
			save = subject.document.save
		except AttributeError:
			print 'WARNING: Could not save; method unavailable'
			raise
		else:
			return save()


	def __focused_block(self, page):
		seg = page.focused_segment
		if seg is not None:
			frag = seg.fragment
			return frag.find_enclosing_model(NotebookBlock)
		else:
			return None


	def __commands__(self):
		return [
			command.Command([command.Key(ord('R'))], 'Insert rich text below', lambda page: self._insert_block(NotebookBlockText(self), True, self.__focused_block(page))),
			command.Command([command.Key(ord('P'))], 'Insert Python code below', lambda page: self._insert_block(NotebookBlockCode(self), True, self.__focused_block(page))),
			command.Command([command.Key(ord('J'))], 'Insert Javascript source below', lambda page: self._insert_block(NotebookBlockSource(self, 'js', 'js'), True, self.__focused_block(page))),
			command.Command([command.Key(ord('C'))], 'Insert CSS source below', lambda page: self._insert_block(NotebookBlockSource(self, 'css', 'css'), True, self.__focused_block(page))),
			command.Command([command.Key(ord('T'))], 'Insert HTML source below', lambda page: self._insert_block(NotebookBlockSource(self, 'html', 'html'), True, self.__focused_block(page))),
			command.Command([command.Key(ord('G'))], 'Insert GLSL source below', lambda page: self._insert_block(NotebookBlockSource(self, 'glsl', 'glsl'), True, self.__focused_block(page))),

			command.Command([command.Key(ord('A')), command.Key(ord('R'))], 'Insert rich text below', lambda page: self._insert_block(NotebookBlockText(self), False, self.__focused_block(page))),
			command.Command([command.Key(ord('A')), command.Key(ord('P'))], 'Insert Python code below', lambda page: self._insert_block(NotebookBlockCode(self), False, self.__focused_block(page))),
			command.Command([command.Key(ord('A')), command.Key(ord('J'))], 'Insert Javascript source below', lambda page: self._insert_block(NotebookBlockSource(self, 'js', 'js'), False, self.__focused_block(page))),
			command.Command([command.Key(ord('A')), command.Key(ord('C'))], 'Insert CSS source below', lambda page: self._insert_block(NotebookBlockSource(self, 'css', 'css'), False, self.__focused_block(page))),
			command.Command([command.Key(ord('A')), command.Key(ord('T'))], 'Insert HTML source below', lambda page: self._insert_block(NotebookBlockSource(self, 'html', 'html'), False, self.__focused_block(page))),
			command.Command([command.Key(ord('A')), command.Key(ord('G'))], 'Insert GLSL source below', lambda page: self._insert_block(NotebookBlockSource(self, 'glsl', 'glsl'), False, self.__focused_block(page))),

			command.Command([command.Key(ord('X'))], 'Remove block', lambda page: self._delete_block(self.__focused_block(page))),
		]

	def __menu_bar_contents__(self, fragment):
		#
		# File menu
		#

		def on_save():
			save_name = self._save_containing_document(fragment)
			fragment.page.page_js_function_call('noty', {'text': 'Saved <em>{0}</em>'.format(save_name), 'type': 'success', 'timeout': 2000, 'layout': 'bottomCenter'})


		save_item = menu.item('Save (Ctrl+S)', lambda: on_save())
		file_menu_contents = menu.sub_menu('File', [save_item])
		file_menu = menu.menu([file_menu_contents], drop_down=True)



		#
		# Edit menu
		#

		def _insert_rich_text(below):
			self._insert_block(NotebookBlockText(self), below, self.__focused_block(fragment.page))

		def _insert_code(below):
			self._insert_block(NotebookBlockCode(self), below, self.__focused_block(fragment.page))

		def _insert_js(below):
			self._insert_block(NotebookBlockSource(self, 'js', 'js'), below, self.__focused_block(fragment.page))

		def _insert_css(below):
			self._insert_block(NotebookBlockSource(self, 'css', 'css'), below, self.__focused_block(fragment.page))

		def _insert_glsl(below):
			self._insert_block(NotebookBlockSource(self, 'glsl', 'glsl'), below, self.__focused_block(fragment.page))

		def _insert_html(below):
			self._insert_block(NotebookBlockSource(self, 'html', 'html'), below, self.__focused_block(fragment.page))

		insert_rich_text_above = menu.item('Insert rich text above', lambda: _insert_rich_text(False))
		insert_code_above = menu.item('Insert executable Python code above', lambda: _insert_code(False))
		insert_js_above = menu.item('Insert JS source above', lambda: _insert_js(False))
		insert_css_above = menu.item('Insert CSS source above', lambda: _insert_css(False))
		insert_html_above = menu.item('Insert HTML source above', lambda: _insert_html(False))
		insert_glsl_above = menu.item('Insert GLSL source above', lambda: _insert_glsl(False))

		insert_rich_text_below = menu.item('Insert rich text below', lambda: _insert_rich_text(True))
		insert_code_below = menu.item('Insert executable Python code below', lambda: _insert_code(True))
		insert_js_below = menu.item('Insert JS source below', lambda: _insert_js(True))
		insert_css_below = menu.item('Insert CSS source below', lambda: _insert_css(True))
		insert_html_below = menu.item('Insert HTML source below', lambda: _insert_html(True))
		insert_glsl_below = menu.item('Insert GLSL source below', lambda: _insert_glsl(True))

		remove_block = menu.item('Remove block', lambda: self._delete_block(self.__focused_block(fragment.page)))
		edit_menu_contents = menu.sub_menu('Edit', [
			insert_rich_text_above,
			insert_code_above,
			insert_js_above,
			insert_css_above,
			insert_html_above,
			insert_glsl_above,

			menu.separator(),

			insert_rich_text_below,
			insert_code_below,
			insert_js_below,
			insert_css_below,
			insert_html_below,
			insert_glsl_below,

			menu.separator(),

			remove_block])

		edit_menu = menu.menu([edit_menu_contents], drop_down=True)

		exec_button = button.button('Execute (Ctrl-Enter)', self.execute)

		return [file_menu, edit_menu, exec_button, self.__execution_state]



	def __present__(self, fragment):
		def on_execute_key(key):
			self.execute()
			return True

		def on_save_key(key):
			save_name = self._save_containing_document(fragment)
			fragment.page.page_js_function_call('noty', {'text': 'Saved <span class="emph">{0}</span>'.format(save_name), 'type': 'success', 'timeout': 2000, 'layout': 'bottomCenter'})



		self.__incr.on_access()



		contents = []

		for block in self.__blocks:
			contents.extend(['<div>', block, '</div>'])


		p = Html(*contents)
		p = p.with_key_handler([KeyAction(KeyAction.KEY_DOWN, 13, ctrl=True)], on_execute_key)
		p = p.with_key_handler([KeyAction(KeyAction.KEY_DOWN, ord('S'), ctrl=True, prevent_default=True)], on_save_key)
		return p.use_css('/static/larch/notebook.css')

