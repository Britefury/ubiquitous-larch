##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.pres.html import Html
from britefury.projection.subject import Subject


from larch.project.project_root import ProjectRoot
from larch.project.project_package import ProjectPackage
from larch.project.project_page import ProjectPage




class Project (object):
	def __init__(self):
		self.__root = ProjectRoot()

		self.__root.append(ProjectPackage('TestPackage', [ProjectPage('PageInPackage', None)]))
		self.__root.append(ProjectPage('PageInIndex', None))



	def __present__(self, fragment):
		contents = [
			'<div class="larch_app_title_bar"><h1 class="page_title">Project</h1></div>',
			self.__root
		]
		return Html(*contents).use_css(url="/project.css")



	def __subject__(self, enclosing_subject, perspective):
		return Subject(enclosing_subject, self, perspective, 'Worksheet')
