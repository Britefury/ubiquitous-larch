##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os
import string
import glob
import pickle
import imp
import sys

from britefury.projection.projection_service import ProjectionService
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from larch.console import console
from larch.worksheet import worksheet
from larch.project import project_root

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
		self.__document_modules = {}


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



	def new_module(self, fullname, loader):
		mod = imp.new_module( fullname )
		#LoadBuiltins.loadBuiltins( mod )
		sys.modules[fullname] = mod
		mod.__file__ = fullname
		mod.__loader__ = loader
		mod.__path__ = fullname.split( '.' )
		self.__document_modules[fullname] = mod
		self.__doc_list._register_imported_module( fullname )
		return mod

	def unload_imported_modules(self, module_fullnames):
		modules = set( module_fullnames )
		modules_to_remove = set( self.__document_modules.keys() ) & modules
		for module_fullname in modules_to_remove:
			del sys.modules[module_fullname]
			del self.__document_modules[module_fullname]
		self.__doc_list._unregister_imported_modules( modules_to_remove )
		return modules_to_remove

	def unload_all_imported_modules(self):
		modules_to_remove = set( self.__document_modules.keys() )
		for module_fullname in modules_to_remove:
			del sys.modules[module_fullname]
		self.__document_modules = {}
		self.__doc_list._unregister_imported_modules( modules_to_remove )
		return modules_to_remove




	def __import_resolve_name(self, finder, name, fullname, path):
		try:
			resolver = finder.__import_resolve__
		except AttributeError:
			return None
		return resolver(name, fullname, path)


	def __import_resolve_model(self, finder, fullname, path):
		while True:
			try:
				__resolve_self__ = finder.__import_resolve_self__
			except AttributeError:
				break
			m = __resolve_self__(fullname, path)
			if m is finder:
				break
			finder = m
		return finder


	def find_module(self, fullname, path=None):
		finder = self.__content
		finder = self.__import_resolve_model(finder, fullname, path)

		names = fullname.split( '.' )
		for name in names:
			finder = self.__import_resolve_name(finder, name, fullname, path)
			if finder is None:
				return None
			finder = self.__import_resolve_model(finder, fullname, path)
			if finder is None:
				return None
		return finder




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



import traceback

class _ImportHookFinderWrapper (object):
	def __init__(self, document,  finder):
		self.__document = document
		self.__finder = finder

	def load_module(self, fullname):
		try:
			return self.__finder.__load_module__(self.__document, fullname)
		except:
			traceback.print_exc()
			raise




class _DocListImportHooks (object):
	def __init__(self, doc_list):
		self.__doc_list = doc_list


	def find_module(self, fullname, path=None):
		try:
			for doc in self.__doc_list:
				finder = doc.find_module(fullname, path)
				if finder is not None:
					return _ImportHookFinderWrapper(doc, finder)
			return None
		except:
			traceback.print_exc()
			raise





class DocumentList (object):
	def __init__(self, path):
		self.__incr = IncrementalValueMonitor()

		self.__path = path

		self.__documents = []
		self.__docs_by_location = {}
		self.__docs_by_filename = {}

		self.__load_documents()

		self.__imported_module_registry = set()

		self.__import_hooks = _DocListImportHooks(self)



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



	def _register_imported_module(self, fullname):
		"""Register a module imported via the import hooks"""
		self.__imported_module_registry.add( fullname )

	def _unregister_imported_modules(self, module_names):
		"""Unregister a set of modules imported via the import hooks"""
		self.__imported_module_registry -= set(module_names)


	def unload_imported_modules(self, module_fullnames):
		"""Unload a list of modules

		Only unloads those imported via the import hooks
		"""
		modules = set(module_fullnames)
		modules_to_remove = self.__imported_module_registry & modules
		for module_fullname in modules_to_remove:
			del sys.modules[module_fullname]
		self.__imported_module_registry -= modules_to_remove
		return modules_to_remove



	def enable_import_hooks(self):
		if self.__import_hooks not in sys.meta_path:
			sys.meta_path.append(self.__import_hooks)





	def __resolve__(self, name, subject):
		doc = self.doc_for_location(name)
		if doc is not None:
			subject.add_step(focus=doc.content, location_trail=[name], document=doc, title=doc.name)
			return doc.content
		else:
			return None




	def __present__(self, fragment):
		self.__incr.on_access()
		contents = ['<table class="larch_app_doc_list">']
		contents.append('<thead class="larch_app_doc_list_header"><td>Title</td><td>Filename</td><td>Save</td></thead>')
		contents.append('<tbody>')
		contents.extend([doc.presentation_table_row()   for doc in self.__documents])
		contents.append('</tbody></table>')
		return Html(*contents)





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



	def __resolve__(self, name, subject):
		try:
			index = int(name)
		except ValueError:
			return None
		if index < 0  or  index > len(self):
			return None
		console = self[index]
		if console is not None:
			subject.add_step(focus=console, location_trail=[name])
			return console
		else:
			return None




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
		self.__docs.enable_import_hooks()
		self.__consoles = ConsoleList()

		self.__doc_gui = GUIList()


	@property
	def docs(self):
		return self.__docs

	@property
	def consoles(self):
		return self.__consoles


	def __resolve__(self, name, subject):
		if name == 'docs':
			subject.add_step(focus=self.__docs, location_trail=[name])
			return self.__docs
		elif name == 'consoles':
			subject.add_step(focus=self.__consoles, location_trail=[name])
			return self.__consoles
		else:
			return None


	def __resolve_self__(self, subject):
		subject.add_step(title='The Ubiquitous Larch')
		return self


	def __present__(self, fragment):
		def _on_reload():
			self.__docs.reload()


		reset_button = button.button('Reload', _on_reload)
		reset_section = Html('<div class="larch_app_menu">', reset_button, '</div>')

		add_worksheet = menu.item('Worksheet', lambda: self.__doc_gui.add(NewDocumentGUI(self.__docs, lambda: worksheet.Worksheet(), 'Worksheet')))
		add_project = menu.item('Project', lambda: self.__doc_gui.add(NewDocumentGUI(self.__docs, lambda: project_root.ProjectRoot(), 'Project')))
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







def create_service(documents_path=None):
	app = LarchApplication(documents_path)

	return ProjectionService(app)
