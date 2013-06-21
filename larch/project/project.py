##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html
from britefury.pres.controls import button, menu, dialog, text_entry

from larch.project.project_root import ProjectRoot




class Project (object):
	def __init__(self):
		self.__root = ProjectRoot()


	@property
	def root(self):
		return self.__root


	def __getstate__(self):
		return {'root' : self.__root}

	def __setstate__(self, state):
		self.__root = state.get('root')



	def __resolve__(self, name, subject):
		subject.add_step(focus=self.__root)
		return self.__root.__resolve__(name, subject)

	def __resolve_self__(self, subject):
		subject.add_step(title='Project')
		return self


	def __present__(self, fragment):
		def _on_set_package_name(name):
			self.__root.python_package_name = name

		python_package_name = self.__root.python_package_name
		python_package_name = python_package_name   if python_package_name is not None  else ''
		entry = text_entry.text_entry(python_package_name, _on_set_package_name)

		contents = [
			'<div class="larch_app_title_bar"><h1 class="page_title">Project</h1></div>',
			'<p class="project_root_package_name">Root package name: ', entry, '<br><span class="notes_text">(this is the base name from which the contents of this project will be importable)</span></p>',
			self.__root,
			'</div>',
		]
		return Html(*contents).use_css(url="/project.css")
