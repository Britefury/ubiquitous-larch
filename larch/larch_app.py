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




larch_app_css = '/larch_app.css'



class AppSubject (Subject):
	def __init__(self, enclosing_subject, app, perspective=None):
		super(AppSubject, self).__init__(enclosing_subject, app, perspective, title='The Ubiquitous Larch')


	def __resolve__(self, name):
		doc = self.focus.docs.doc_for_name(name)
		if doc is not None:
			return doc.__subject__(self, self.perspective)
		else:
			return None





class DocumentList (object):
	def __init__(self):
		self.__documents = []
		self.__documents_by_name = {}
		self.__incr = IncrementalValueMonitor()

		w = worksheet.Worksheet()
		self.__documents.append(w)
		self.__documents_by_name['w'] = w


	def __iter__(self):
		return iter(self.__documents)


	def doc_for_name(self, name):
		return self.__documents_by_name.get(name)

	def __present__(self, fragment):
		self.__incr.on_access()
		html1 = '<ul>'
		html2 = '</ul>'
		return Html(html1, html2)




class LarchApplication (object):
	def __init__(self):
		self.__docs = DocumentList()


	@property
	def docs(self):
		return self.__docs


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


	def __subject__(self, enclosing_subject, perspective):
		return AppSubject(enclosing_subject, self, perspective)







def create_service():
	focus = LarchApplication()
	index_subject = Subject.subject_for(None, focus)


	def _initialise_document(dynamic_document, location):
		subject = index_subject.resolve(location)
		print 'Got a subject {0} for the location {1}'.format(subject, location)
		if subject is not None:
			return IncrementalView(subject, dynamic_document)
		else:
			return None


	return DynamicDocumentService(_initialise_document)
