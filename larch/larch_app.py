##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os
import string

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
		doc = self.focus.docs.doc_for_location(name)
		if doc is not None:
			return doc.content.__subject__(self, self.perspective)
		else:
			return None




class Document (object):
	def __init__(self, name, content):
		self.__name = name
		loc = ''.join([x   for x in name   if x in string.ascii_letters + string.digits + '_'])
		self.__loc = loc
		self.__content = content


	@property
	def name(self):
		return self.__name

	@property
	def location(self):
		return self.__loc

	@property
	def content(self):
		return self.__content



	def __present__(self, fragment):
		return Html('<p><a href="/pages/{0}">{1}</p>'.format(self.__loc, self.__name))





class DocumentList (object):
	def __init__(self):
		self.__documents = []
		self.__docs_by_location = {}
		self.__incr = IncrementalValueMonitor()

		w = worksheet.Worksheet()
		self.add_document_for_content('w', w)


	def __iter__(self):
		return iter(self.__documents)


	def doc_for_location(self, name):
		return self.__docs_by_location.get(name)



	def add_document(self, doc):
		self.__documents.append(doc)
		self.__docs_by_location[doc.location] = doc
		self.__incr.on_changed()

	def add_document_for_content(self, name, content):
		self.add_document(Document(name, content))



	def __present__(self, fragment):
		self.__incr.on_access()
		contents = ['<div>']
		contents.extend(self.__documents)
		contents.append('</div>')
		return Html(*contents)




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
		if subject is not None:
			return IncrementalView(subject, dynamic_document)
		else:
			return None


	return DynamicDocumentService(_initialise_document)
