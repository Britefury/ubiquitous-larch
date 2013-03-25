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
from britefury.pres.controls import menu




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
		return Html('<p class="larch_app_doc"><a href="/pages/{0}">{1}</a></p>'.format(self.__loc, self.__name))





class DocumentList (object):
	def __init__(self):
		self.__documents = []
		self.__docs_by_location = {}
		self.__incr = IncrementalValueMonitor()


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
		contents = ['<div class="larch_app_doc_list">']
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
		add_worksheet = menu.item('Worksheet', lambda: self.__docs.add_document_for_content('Worksheet', worksheet.Worksheet()))
		new_item = menu.sub_menu('New', [add_worksheet])

		new_menu = menu.menu([new_item], drop_down=True)
		new_menu = Html('<div class="larch_app_menu">', new_menu, '</div>')


		contents = ["""
			<div class="larch_app_enclosure">
				<div class="larch_app_title_bar"><h1 class="larch_app_title">The Ubiquitous Larch</h1></div>

				<h2>Open documents:</h2>
			""",
			self.__docs,
			new_menu,
			"""
			</div>
			<p class="larch_app_powered_by">Powered by
			<a class="larch_app_pwr_link" href="http://www.python.org">Python</a>,
			<a class="larch_app_pwr_link" href="http://flask.pocoo.org">Flask</a>/<a class="larch_app_pwr_link" href="http://bottlepy.org">Bottle</a>/<a class="larch_app_pwr_link" href="http://www.cherrypy.org/">CherryPy</a>,
			<a class="larch_app_pwr_link" href="http://jquery.com/">jQuery</a>,
			<a class="larch_app_pwr_link" href="http://www.json.org/js.html">json.js</a>,
			<a class="larch_app_pwr_link" href="http://codemirror.net/">Code Mirror</a>,
			<a class="larch_app_pwr_link" href="http://ckeditor.com/">ckEditor</a>,
			<a class="larch_app_pwr_link" href="http://lokeshdhakar.com/projects/lightbox2/">Lightbox 2</a>,
			<a class="larch_app_pwr_link" href="http://d3js.org/">d3.js</a>, and
			<a class="larch_app_pwr_link" href="http://bartaz.github.com/impress.js/#/bored">impress.js</a></p>
			"""]
		return Html(*contents).use_css(url=larch_app_css)



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
