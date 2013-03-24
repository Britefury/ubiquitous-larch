##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp
import _ast
import sys
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.pres.html import Html
from britefury.pres.key_event import Key
from britefury.pres.controls import ckeditor, menu, button
from britefury.projection.subject import Subject
from larch.python import PythonCode


__author__ = 'Geoff'


class WorksheetBlock (object):
	def __init__(self, worksheet):
		self._worksheet = worksheet


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


	def __present__(self, fragment):
		self.__incr.on_access()

		p = ckeditor.ckeditor(self.__text, on_focus=self._on_focus)

		return Html('<div class="worksheet_block">', p, '</div>')



class WorksheetBlockCode (WorksheetBlock):
	def __init__(self, worksheet, code=None):
		super(WorksheetBlockCode, self).__init__(worksheet)
		if code is None:
			code = PythonCode()
		else:
			assert isinstance(code, PythonCode)
		self.__code = code
		self.__code.on_focus = self._on_focus
		self.__result = None
		self.__incr = IncrementalValueMonitor()


	def execute(self, module):
		self.__result = self.__code.execute_in_module(module)
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()
		code = Html('<div class="worksheet_code_container">', self.__code, '</div>')
		res = ['<div>', self.__result, '</div>']   if self.__result is not None  else []
		return Html(*(['<div class="worksheet_block">', code] + res + ['</div>']))




class Worksheet (object):
	def __init__(self, code=''):
		self.__blocks = [WorksheetBlockCode(self)]
		self.__incr = IncrementalValueMonitor()
		self._module = None
		self.__focus_block = None


	def execute(self):
		self._module = imp.new_module('<Worksheet>')
		for block in self.__blocks:
			block.execute(self._module)



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


	def __present__(self, fragment):
		def on_execute():
			self.execute()

		def on_execute_key(key):
			self.execute()
			return True


		self.__incr.on_access()

		contents = []


		def _insert_code(below):
			self._insert_block(WorksheetBlockCode(self), below)

		def _insert_rich_text(below):
			self._insert_block(WorksheetBlockText(self), below)


		insert_code_above_button = button.button('Insert code above', lambda: _insert_code(False))

		insert_code_above = menu.item('Insert code above', lambda: _insert_code(False))
		insert_rich_text_above = menu.item('Insert rich text above', lambda: _insert_rich_text(False))

		insert_code_below = menu.item('Insert code below', lambda: _insert_code(True))
		insert_rich_text_below = menu.item('Insert rich text below', lambda: _insert_rich_text(True))
		blocks_menu = menu.sub_menu('Worksheet', [insert_code_above, insert_rich_text_above, menu.item('--------', None), insert_code_below, insert_rich_text_below])

		page_menu = menu.menu([blocks_menu], drop_down=True)
		contents.append(Html('<div class="worksheet_menu_bar">', page_menu, '</div>'))

		for block in self.__blocks:
			contents.extend(['<div>', block, '</div>'])

		contents.append(Html('<div><p>Powered by jQuery, Code Mirror, ckEditor, etc....</p></div>'))

		p = Html(*contents)
		p = p.with_key_handler([Key(Key.KEY_DOWN, 13, ctrl=True)], on_execute_key)
		return p.use_css('/worksheet.css')


	def __subject__(self, enclosing_subject, perspective):
		return Subject(enclosing_subject, self, perspective, 'Worksheet')

