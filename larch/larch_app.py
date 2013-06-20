##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os
import string
import glob
import pickle

from britefury.projection.subject import Subject
from britefury.projection.projection_service import ProjectionService
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from larch.console import console
from larch.worksheet import worksheet
from larch.project import project

from britefury.pres.html import Html
from britefury.pres.controls import menu, button, dialog, text_entry




_EXTENSION = '.ularch'



class DocumentNameInUseError (object):
	pass




def load_document(path):
	with open(path, 'rU') as f:
		return pickle.load(f)

def save_document(path, content):
	with open(path, 'w') as f:
		pickle.dump(content, f)




larch_app_css = '/larch_app.css'




class AppSubject (Subject):
	def __init__(self, enclosing_subject, location_trail, app, perspective=None):
		super(AppSubject, self).__init__(enclosing_subject, location_trail, app, perspective, title='The Ubiquitous Larch')
		self.docs = DocListSubject(self, ['docs'], app.docs, perspective)
		self.consoles = ConsoleListSubject(self, ['consoles'], app.consoles, perspective)


	def __resolve__(self, name):
		if name == 'docs':
			return self.docs
		elif name == 'consoles':
			return self.consoles
		else:
			return None




_filename_chars = string.ascii_letters + string.digits + ' _-'

def _sanitise_filename_char(x):
	return x   if x in _filename_chars   else '_'

def _sanitise_filename(name):
	return ''.join([_sanitise_filename_char(x)  for x in name])



class Document (object):
	def __init__(self, doc_list, name, filename, content):
		self.__doc_list = doc_list
		self.__name = name
		self.__filename = filename
		loc = ''.join([x   for x in name   if x in string.ascii_letters + string.digits + '_'])
		self.__loc = loc
		self.__content = content


	@property
	def name(self):
		return self.__name

	@property
	def filename(self):
		return self.__filename

	@property
	def location(self):
		return self.__loc

	@property
	def content(self):
		return self.__content




	def save(self):
		file_path = os.path.join(self.__doc_list.path, self.__filename + _EXTENSION)
		save_document(file_path, self.__content)


	def presentation_table_row(self):
		def on_save():
			self.save()

		save_button = button.button('Save', on_save)
		doc_title = '<a href="/pages/docs/{0}" class="larch_app_doc_title">{1}</a>'.format(self.__loc, self.__name)
		doc_filename = '<span class="larch_app_doc_filename">{0}</span><span class="larch_app_doc_extension">.ularch</span>'.format(self.__filename)
		controls = Html('<div class="larch_app_doc_controls">', save_button, '</div>')
		return Html('<tr class="larch_app_doc">	<td>', doc_title, '</td><td>', doc_filename, '</td><td>', controls, '</td></tr>')




class _DocSubject (Subject):
	def __init__(self, enclosing_subject, location_trail, doc, perspective=None):
		super(_DocSubject, self).__init__(enclosing_subject, location_trail, doc, perspective, title=doc.name)


	def save(self):
		self.focus.save()




class DocListSubject (Subject):
	def __init__(self, enclosing_subject, location_trail, docs, perspective=None):
		super(DocListSubject, self).__init__(enclosing_subject, location_trail, docs, perspective, title='The Ubiquitous Larch')


	def __resolve__(self, name):
		doc = self.focus.doc_for_location(name)
		if doc is not None:
			doc_subj = _DocSubject(self, [name], doc, self.perspective)
			return doc.content.__subject__(doc_subj, [], self.perspective)
		else:
			return None




class DocumentList (object):
	def __init__(self, path):
		self.__incr = IncrementalValueMonitor()

		self.__path = path

		self.__documents = []
		self.__docs_by_location = {}
		self.__docs_by_filename = {}

		self.__load_documents()



	@property
	def path(self):
		return self.__path


	def __iter__(self):
		return iter(self.__documents)


	def doc_for_location(self, location):
		return self.__docs_by_location.get(location)

	def doc_for_filename(self, filename):
		return self.__docs_by_filename.get(filename)



	def __add_document(self, doc):
		self.__documents.append(doc)
		self.__docs_by_location[doc.location] = doc
		self.__docs_by_filename[doc.filename] = doc
		self.__incr.on_changed()

	def new_document_for_content(self, name, content):
		if name in self.__docs_by_filename:
			raise DocumentNameInUseError, name
		doc = Document(self, name, _sanitise_filename(name), content)
		doc.save()
		self.__add_document(doc)


	def save_all(self):
		for doc in self.__documents:
			doc.save()


	def reload(self):
		self.__documents = []
		self.__docs_by_location = {}
		self.__docs_by_filename = {}

		self.__load_documents()

		self.__incr.on_changed()



	def __load_documents(self):
		file_paths = glob.glob(os.path.join(self.__path, '*' + _EXTENSION))
		for p in sorted(file_paths):
			directory, filename = os.path.split(p)
			name, ext = os.path.splitext(filename)
			content = load_document(p)
			doc = Document(self, name, name, content)
			self.__add_document(doc)





	def __present__(self, fragment):
		self.__incr.on_access()
		contents = ['<table class="larch_app_doc_list">']
		contents.append('<thead class="larch_app_doc_list_header"><td>Title</td><td>Filename</td><td>Save</td></thead>')
		contents.append('<tbody>')
		contents.extend([doc.presentation_table_row()   for doc in self.__documents])
		contents.append('</tbody></table>')
		return Html(*contents)



class ConsoleListSubject (Subject):
	def __init__(self, enclosing_subject, location_trail, consoles, perspective=None):
		super(ConsoleListSubject, self).__init__(enclosing_subject, location_trail, consoles, perspective, title='The Ubiquitous Larch')


	def __resolve__(self, name):
		try:
			index = int(name)
		except ValueError:
			return None
		if index < 0  or  index > len(self.focus):
			return None
		console = self.focus[index]
		if console is not None:
			return console.__subject__(self, [name], self.perspective)
		else:
			return None




class ConsoleList (object):
	def __init__(self):
		self.__consoles = []
		self.__incr = IncrementalValueMonitor()



	def __getitem__(self, item):
		return self.__consoles[item]

	def __len__(self):
		return len(self.__consoles)

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





class GUIBox (object):
	def __init__(self):
		self._gui_list = None


	def close(self):
		self._gui_list.close(self)



class DocNameInUseGui (GUIBox):
	def __init__(self, filename):
		super(DocNameInUseGui, self).__init__()
		self.filename = filename

	def __present__(self, fragment):
		return Html('<div class="larch_app_doc_name_in_use"><p class="error_text">There is already a document in a file named \'{0}<span class="emph">.ularch</span>\'.</p>'.format(self.filename),
			    button.button('Close', self.close), '</div>')


class NewDocumentGUI (GUIBox):
	def __init__(self, doc_list, document_factory, initial_name):
		super(NewDocumentGUI, self).__init__()
		self.__doc_list = doc_list
		self.__document_factory = document_factory
		self.__name = initial_name


	def __present__(self, fragment):
		def on_edit(text):
			self.__name = text

		def on_create():
			filename = _sanitise_filename(self.__name)
			if self.__doc_list.doc_for_filename(filename) is not None:
				self._gui_list.add(DocNameInUseGui(filename))
			else:
				document = self.__document_factory()
				self.__doc_list.new_document_for_content(self.__name, document)
			self.close()

		def on_cancel():
			self.close()

		return Html('<div class="gui_box">',
				'<span class="gui_section_1">Create document</span><br>',
				'<table>',
				'<tr><td><span class="gui_label">Name:</span></td><td>', text_entry.text_entry(self.__name, on_edit=on_edit), '</td></tr>',
				'<tr><td>', button.button('Cancel', on_cancel), '</td><td>', button.button('Create', on_create), '</td></tr>',
				'</table>',
				'</div>')



class GUIList (object):
	def __init__(self):
		self.contents = []
		self.__incr = IncrementalValueMonitor()


	def add(self, box):
		box._gui_list = self
		self.contents.append(box)
		self.__incr.on_changed()


	def close(self, box):
		self.contents.remove(box)
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()
		return Html(*self.contents)




class LarchApplication (object):
	def __init__(self, documents_path=None):
		if documents_path is None:
			documents_path = os.getcwd()

		self.__documents_path = documents_path

		self.__docs = DocumentList(documents_path)
		self.__consoles = ConsoleList()

		self.__doc_gui = GUIList()


	@property
	def docs(self):
		return self.__docs

	@property
	def consoles(self):
		return self.__consoles


	def __present__(self, fragment):
		def _on_reload():
			self.__docs.reload()


		reset_button = button.button('Reload', _on_reload)
		reset_section = Html('<div class="larch_app_menu">', reset_button, '</div>')

		add_worksheet = menu.item('Worksheet', lambda: self.__doc_gui.add(NewDocumentGUI(self.__docs, lambda: worksheet.Worksheet(), 'Worksheet')))
		add_project = menu.item('Project', lambda: self.__doc_gui.add(NewDocumentGUI(self.__docs, lambda: project.Project(), 'Project')))
		new_item = menu.sub_menu('New', [add_worksheet, add_project])

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
			reset_section,
			self.__docs,
			new_document_menu,
			self.__doc_gui,
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



	def __subject__(self, enclosing_subject, location_trail, perspective):
		return AppSubject(enclosing_subject, location_trail, self, perspective)







def create_service(documents_path=None):
	focus = LarchApplication(documents_path)
	index_subject = Subject.subject_for(None, ['pages'], focus)

	return ProjectionService(index_subject)
