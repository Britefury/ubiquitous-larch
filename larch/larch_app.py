##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os

from britefury.dynamicsegments.service import DynamicDocumentService

from britefury.projection.subject import Subject
from britefury.incremental_view.incremental_view import IncrementalView
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from larch.console import console
from larch.worksheet import worksheet

from britefury.pres.html import Html




larch_app_css = 'larch_app.css'



class DocumentList (object):
	def __init__(self):
		self.__documents = []
		self.__incr = IncrementalValueMonitor()


	def __present__(self, fragment):
		self.__incr.on_access()
		html1 = '<ul>'
		html2 = '</ul>'
		return Html(html1, html2)


class LarchApplication (object):
	def __init__(self):
		self.__docs = DocumentList()



	def __present__(self, fragment):
		html1 = """
		<div class="larch_app_enclosure">
			<div class="larch_app_title_bar"><h1 class="larch_app_title">The Ubiquitous Larch</h1></div>

			<h2>Open documents:</h2>
		"""
		html2 = """
		</div>
		"""
		return Html(html1, self.__docs, html2).use_css(url=larch_app_css)







def create_service():
	focus = LarchApplication()
	index_subject = Subject(None, focus, title='The Ubiquitous Larch')


	def _initialise_document(dynamic_document, location):
		subject = index_subject.resolve(location)
		if subject is not None:
			return IncrementalView(subject, dynamic_document)
		else:
			return None


	return DynamicDocumentService(_initialise_document)
