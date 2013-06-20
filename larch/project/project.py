##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html
from britefury.pres.controls import button, menu, dialog, text_entry
from britefury.projection.subject import Subject

from britefury.live.live_value import LiveValue

from larch.project.project_root import ProjectRoot
from larch.project.project_package import ProjectPackage
from larch.project.project_page import ProjectPage




class Project (object):
	def __init__(self):
		self.__root = ProjectRoot()


	def __getstate__(self):
		return {'root' : self.__root}

	def __setstate__(self, state):
		self.__root = state.get('root')



	def __present__(self, fragment):
		contents = [
			'<div class="larch_app_title_bar"><h1 class="page_title">Project</h1></div>',
			self.__root,
			'</div>',
		]
		return Html(*contents).use_css(url="/project.css")



	def __subject__(self, enclosing_subject, perspective):
		return Subject(enclosing_subject, self, perspective, 'Worksheet')
