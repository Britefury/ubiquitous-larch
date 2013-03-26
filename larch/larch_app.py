##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os
import string
import glob
import pickle

from britefury.dynamicsegments.service import DynamicDocumentService

from britefury.projection.subject import Subject
from britefury.incremental_view.incremental_view import IncrementalView
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from larch.console import console
from larch.worksheet import worksheet

from britefury.pres.html import Html
from britefury.pres.controls import menu, button




_EXTENSION = '.ularch'

def load_document(path):
	with open(path, 'rU') as f:
		return pickle.load(f)

def save_document(path, content):
	with open(path, 'w') as f:
		pickle.dump(content, f)




larch_app_css = '/larch_app.css'




class AppSubject (Subject):
	def __init__(self, enclosing_subject, app, perspective=None):
		super(AppSubject, self).__init__(enclosing_subject, app, perspective, title='The Ubiquitous Larch')
		self.docs = DocListSubject(self, app.docs, perspective)
		self.consoles = ConsoleListSubject(self, app.consoles, perspective)


	def __resolve__(self, name):
		if name == 'docs':
			return self.docs
		elif name == 'consoles':
			return self.consoles
		else:
			return None





class Document (object):
	def __init__(self, doc_list, name, content):
		self.__doc_list = doc_list
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




	def save(self):
		file_path = os.path.join(self.__doc_list.path, self.__name + _EXTENSION)
		save_document(file_path, self.__content)


	def __present__(self, fragment):
		def on_save():
			self.save()

		save_button = button.button('Save', on_save)
		doc_link = '<a href="/pages/docs/{0}">{1}</a>'.format(self.__loc, self.__name)
		return Html('<p class="larch_app_doc">', doc_link, save_button, '</p>')




class DocListSubject (Subject):
	def __init__(self, enclosing_subject, docs, perspective=None):
		super(DocListSubject, self).__init__(enclosing_subject, docs, perspective, title='The Ubiquitous Larch')


	def __resolve__(self, name):
		doc = self.focus.doc_for_location(name)
		if doc is not None:
			return doc.content.__subject__(self, self.perspective)
		else:
			return None




class DocumentList (object):
	def __init__(self, path):
		self.__path = path
		self.__documents = []
		self.__docs_by_location = {}
		self.__incr = IncrementalValueMonitor()

		file_paths = glob.glob(os.path.join(path, '*' + _EXTENSION))
		for p in file_paths:
			directory, filename = os.path.split(p)
			name, ext = os.path.splitext(filename)
			content = load_document(p)
			doc = Document(self, name, content)
			self.__add_document(doc)



	@property
	def path(self):
		return self.__path


	def __iter__(self):
		return iter(self.__documents)


	def doc_for_location(self, name):
		return self.__docs_by_location.get(name)



	def __add_document(self, doc):
		self.__documents.append(doc)
		self.__docs_by_location[doc.location] = doc
		self.__incr.on_changed()

	def new_document_for_content(self, name, content):
		doc = Document(self, name, content)
		doc.save()
		self.__add_document(doc)


	def save_all(self):
		for doc in self.__documents:
			doc.save()



	def __present__(self, fragment):
		self.__incr.on_access()
		contents = ['<div class="larch_app_doc_list">']
		contents.extend(self.__documents)
		contents.append('</div>')
		return Html(*contents)



class ConsoleListSubject (Subject):
	def __init__(self, enclosing_subject, consoles, perspective=None):
		super(ConsoleListSubject, self).__init__(enclosing_subject, consoles, perspective, title='The Ubiquitous Larch')


	def __resolve__(self, name):
		try:
			index = int(name)
		except ValueError:
			return None
		console = self.focus[index]
		if console is not None:
			return console.__subject__(self, self.perspective)
		else:
			return None




class ConsoleList (object):
	def __init__(self):
		self.__consoles = []
		self.__incr = IncrementalValueMonitor()



	def __getitem__(self, item):
		return self.__consoles[item]

	def new_console(self):
		con = console.Console()
		self.__consoles.append(con)
		self.__incr.on_changed()



	def __present__(self, fragment):
		self.__incr.on_access()
		contents = ['<div class="larch_app_console_list">']
		for i, con in enumerate(self.__consoles):
			console_link = '<p class="larch_app_console"><a href="/pages/consoles/{0}">Console {0}</a></p>'.format(i)
			contents.append( console_link)
		contents.append('</div>')
		return Html(*contents)




class LarchApplication (object):
	def __init__(self, documents_path=None):
		if documents_path is None:
			documents_path = os.getcwd()

		self.__docs = DocumentList(documents_path)
		self.__consoles = ConsoleList()


	@property
	def docs(self):
		return self.__docs

	@property
	def consoles(self):
		return self.__consoles


	def __present__(self, fragment):
		add_worksheet = menu.item('Worksheet', lambda: self.__docs.new_document_for_content('Worksheet', worksheet.Worksheet()))
		new_item = menu.sub_menu('New', [add_worksheet])

		new_document_menu = menu.menu([new_item], drop_down=True)
		new_document_menu = Html('<div class="larch_app_menu">', new_document_menu, '</div>')


		def on_new_console():
			self.__consoles.new_console()


		new_console_button = button.button('New console', on_new_console)


		contents = ["""
			<div class="larch_app_enclosure">
				<div class="larch_app_title_bar"><h1 class="larch_app_title">The Ubiquitous Larch</h1></div>

				<section class="larch_app_docs_section">
				<h2>Open documents:</h2>
			""",
			self.__docs,
			new_document_menu,
			"""</section>
			<section class="larch_app_consoles_section">
				<h2>Consoles:</h2>
			""",
			self.__consoles,
			new_console_button,
			"""
			</section>
			<p class="larch_app_powered_by">Powered by
			<a class="larch_app_pwr_link" href="http://www.python.org">Python</a>,
			<a class="larch_app_pwr_link" href="http://flask.pocoo.org">Flask</a>/<a class="larch_app_pwr_link" href="http://bottlepy.org">Bottle</a>/<a class="larch_app_pwr_link" href="http://www.cherrypy.org/">CherryPy</a>,
			<a class="larch_app_pwr_link" href="http://jquery.com/">jQuery</a>,
			<a class="larch_app_pwr_link" href="http://www.json.org/js.html">json.js</a>,
			<a class="larch_app_pwr_link" href="http://codemirror.net/">Code Mirror</a>,
			<a class="larch_app_pwr_link" href="http://ckeditor.com/">ckEditor</a>,
			<a class="larch_app_pwr_link" href="http://lokeshdhakar.com/projects/lightbox2/">Lightbox 2</a>,
			<a class="larch_app_pwr_link" href="http://d3js.org/">d3.js</a>, and
			<a class="larch_app_pwr_link" href="http://bartaz.github.com/impress.js/">impress.js</a></p>
			</div>
			"""]
		return Html(*contents).use_css(url=larch_app_css)



	def __subject__(self, enclosing_subject, perspective):
		return AppSubject(enclosing_subject, self, perspective)







def create_service(documents_path=None):
	focus = LarchApplication(documents_path)
	index_subject = Subject.subject_for(None, focus)


	def _initialise_document(dynamic_document, location):
		subject = index_subject.resolve(location)
		if subject is not None:
			return IncrementalView(subject, dynamic_document)
		else:
			return None


	return DynamicDocumentService(_initialise_document)
