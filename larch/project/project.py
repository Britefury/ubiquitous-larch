##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import imp

from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.pres.html import Html
from britefury.pres.key_event import Key
from britefury.pres.controls import ckeditor, menu, button
from britefury.projection.subject import Subject
from britefury.live.live_value import LiveValue
from larch.python import PythonCode



class ProjectNode (object):
	def __init__(self, name):
		self._name = name
		self._parent = None


	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, n):
		self._name = n



class ProjectPage (ProjectNode):
	pass



class ProjectPackage (ProjectNode):
	pass





class Project (object):
	def __init__(self):
		pass


	def __present__(self, fragment):
		return Html("""
		<div class="larch_app_title_bar"><h1 class="page_title">Project</h1></div>
		""")



	def __subject__(self, enclosing_subject, perspective):
		return Subject(enclosing_subject, self, perspective, 'Worksheet')
