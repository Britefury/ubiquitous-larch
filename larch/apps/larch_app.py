##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import os
import string
import glob
import pickle
import imp
import sys
import urllib2
from optparse import OptionParser
from larch.apps.notebook import ipynb_filter
from larch.apps.project import project_root
from larch.apps.notebook import notebook

from larch.core.projection_service import ProjectionService
from larch.incremental import IncrementalValueMonitor
from larch import command
from larch.apps.console import console
from larch.controls import form, button, menu, text_entry, noty
from larch.live import LiveValue
from larch.pres.pres import CompositePres
from larch.pres.html import Html


_EXTENSION = '.ularch'



class DocumentNameInUseError (object):
	pass




larch_app_css = '/static/larch/larch_app.css'





_filename_chars = string.ascii_letters + string.digits + ' _-.'

def _sanitise_filename_char(x):
	return x   if x in _filename_chars   else '_'

def _sanitise_filename(name):
	return ''.join([_sanitise_filename_char(x)  for x in name])





#
#
# PAGE FRAME
#
#


class PageFrame (CompositePres):
	def __init__(self, subject, logout_url_path, documentation_url):
		self.__page = subject.focus
		self.__focii = subject.focii
		self.__logout_url_path = logout_url_path
		self.__documentation_url = documentation_url



	def __menu_bar_contents_to_table(self, menu_bar_contents):
		# Generate the menu bar
		if len(menu_bar_contents) > 0:
			contents = ['<table><tr>']
			for x in menu_bar_contents:
				contents.extend(['<td class="__larch_app_frame_menu_bar">', x, '</td>'])
			contents.append('</tr></table>')
			return Html(*contents)
		else:
			return Html()

	def pres(self, pres_ctx):
		fragment = pres_ctx.fragment_view

		menu_bar_contents = []
		right_menu_bar_contents = []

		# Liveliness indicator
		def _toggle_liveliness(event_name, ev_data):
			pres_ctx.fragment_view.page.page_js_function_call('larch.toggleLiveliness')

		liveliness_indicator = Html('<div class="larch_liveliness_indicator larch_liveliness_off">LIVE</div>').js_function_call('larch.initLivelinessToggle')
		right_menu_bar_contents.append(liveliness_indicator)

		# Documentation
		if self.__documentation_url is not None:
			doc_link = Html('<a class="__larch_app_doc_link" href="{0}">Documentation</a>'.format(self.__documentation_url))
			right_menu_bar_contents.append(doc_link)

		# Command bar button
		cmd_bar_button = Html('<button class="__larch_app_cmd_bar_button">Cmd. bar (Esc)</button>').js_function_call("larch.controls.initToggleCommandBarButton")
		right_menu_bar_contents.append(cmd_bar_button)

		# Logout link
		if self.__logout_url_path is not None:
			#right_menu_bar_contents.append(Html('<div class="__larch_app_frame_logout_link"><a href="{0}">Logout</a></div>'.format(self.__logout_url_path)))
			right_menu_bar_contents.append(Html('<a href="{0}">Logout</a>'.format(self.__logout_url_path)).js_eval('$(node).button();'))

		# Build the menu bar contents by iterating through the focii, accumulating them as we go by concatenating the results of calling the __menu_bar_cumulative_contents__ method
		for f in self.__focii:
			try:
				method = f.__menu_bar_cumulative_contents__
			except AttributeError:
				pass
			else:
				menu_bar_contents.extend(method(fragment))

		# Add the result of calling __menu_bar_contents__ on the final focus
		try:
			method = self.__page.__menu_bar_contents__
		except AttributeError:
			pass
		else:
			menu_bar_contents.extend(method(fragment))

		# Generate the menu bar
		main_menu_bar = self.__menu_bar_contents_to_table(menu_bar_contents)
		right_menu_bar = self.__menu_bar_contents_to_table(right_menu_bar_contents)

		return Html(
			'<div class="__larch_app_frame_page_header">',
			'<span class="__larch_cmd_bar_right">',
			right_menu_bar,
			'</span>',
			main_menu_bar,
			'</div>',
			'<img src="/static/1px_transparent.png">',
			'<div class="larch_frame_page_content">',
			self.__page,
			'</div>'
		).use_css(url='/static/larch/larch_app_frame.css')



def _make_apply_page_frame(logout_url_path, documentation_url):
	def _apply_page_frame(subject):
		return PageFrame(subject, logout_url_path, documentation_url)
	return _apply_page_frame




#
#
# IMPORTED MODULE REGISTRY
#
#

class ImportedModuleRegistry (object):
	def __init__(self):
		self.__imported_module_registry = set()

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




class Document (object):
	def __init__(self, doc_list, name, filename, content, imported_module_registry=None):
		if imported_module_registry is None:
			imported_module_registry = ImportedModuleRegistry()
		self.__imported_module_registry = imported_module_registry

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
		self.__imported_module_registry._register_imported_module( fullname )
		return mod

	def unload_imported_modules(self, module_fullnames):
		modules = set(module_fullnames)
		modules_to_remove = set(self.__document_modules.keys()) & modules
		for module_fullname in modules_to_remove:
			del sys.modules[module_fullname]
			del self.__document_modules[module_fullname]
		self.__imported_module_registry._unregister_imported_modules( modules_to_remove )
		return modules_to_remove

	def unload_all_imported_modules(self):
		modules_to_remove = set(self.__document_modules.keys())
		for module_fullname in modules_to_remove:
			del sys.modules[module_fullname]
		self.__document_modules = {}
		self.__imported_module_registry._unregister_imported_modules( modules_to_remove )
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


	def unload_modules_and_display_notification(self, display_on):
		modules_removed = self.unload_all_imported_modules()
		if len(modules_removed) > 0:
			mods = ', '.join(['<em>{0}</em>'.format(name)   for name in modules_removed])
			noty.noty(Html('Unloaded the following modules: {0}'.format(mods)), type='success', timeout=2000, layout='bottomCenter').show_on(display_on)
		else:
			noty.noty(Html('No modules to unload'), type='success', timeout=2000, layout='bottomCenter').show_on(display_on)



	def save_and_display_notification(self, display_on):
		name = self.save()
		noty.noty(Html('Saved <em>{0}</em>'.format(name)), type='success', timeout=2000, layout='bottomCenter').show_on(display_on)



	def __on_save_command(self, page):
		self.save_and_display_notification(page)



	def __on_unload_modules_command(self, page):
		self.unload_modules_and_display_notification(page)



	def __commands__(self):
		return [
			command.Command([command.Key(ord('S'))], 'Save', self.__on_save_command),
			command.Command([command.Key(ord('U'))], 'Unload modules', self.__on_unload_modules_command),
		]


	def __resolve_self__(self, subject):
		subject.add_step(focus=self.content)
		return self.content



	def save(self):
		file_path = os.path.join(self.__doc_list.path, self.__filename + _EXTENSION)
		# Convert to string first, in case we encounter an exception while pickling
		# This way, the save process bails *before* overwriting the file with nonsense
		s = pickle.dumps(self.__content)
		with open(file_path, 'w') as f:
			f.write(s)
		return self.__filename


	@staticmethod
	def load(app, doc_list, path, imported_module_registry):
		doc = app._get_document_for_path(path)
		if doc is None:
			try:
				with open(path, 'rU') as f:
					content = pickle.load(f)
			except:
				print 'Error: could not load {0}: {1}'.format(path, sys.exc_info())
			else:
				filename = os.path.split(path)[1]
				name = os.path.splitext(filename)[0]
				doc = Document(doc_list, name, name, content, imported_module_registry)
				app._set_document_for_path(path, doc)
				return doc
		else:
			return doc




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
	def __init__(self, app, path, loc_prefix):
		self.__incr = IncrementalValueMonitor()

		self.__imported_module_registry = ImportedModuleRegistry()

		self._app = app
		self.__path = path
		self.__loc_prefix = loc_prefix

		self.__documents = []
		self.__docs_by_location = {}
		self.__docs_by_filename = {}

		self.__load_documents()

		self.__import_hooks = _DocListImportHooks(self)



	@property
	def path(self):
		return self.__path

	@property
	def loc_prefix(self):
		return self.__loc_prefix


	def __iter__(self):
		return iter(self.__documents)


	def doc_for_location(self, location):
		return self.__docs_by_location.get(location)

	def doc_for_filename(self, filename):
		return self.__docs_by_filename.get(filename)

	def unused_filename(self, filename):
		if filename not in self.__docs_by_filename:
			return filename

		index = 0
		while True:
			name = filename + '_' + str(index)
			if name not in self.__docs_by_filename:
				return name
			index += 1


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


	def reload(self):
		self.__documents = []
		self.__docs_by_location = {}
		self.__docs_by_filename = {}

		self.__load_documents()

		self.__incr.on_changed()



	def __load_documents(self):
		file_paths = glob.glob(os.path.join(self.__path, '*' + _EXTENSION))
		for p in sorted(file_paths):
			doc = Document.load(self._app, self, p, self.__imported_module_registry)
			if doc is not None:
				self.__add_document(doc)



	def enable_import_hooks(self):
		if self.__import_hooks not in sys.meta_path:
			sys.meta_path.append(self.__import_hooks)





	def __resolve__(self, name, subject):
		doc = self.doc_for_location(name)
		if doc is not None:
			subject.add_step(focus=doc, location_trail=[name], document=doc, title=doc.name)
			return doc
		else:
			return None



	def __doc_table_row(self, doc, page):
		def on_save(event):
			doc.save_and_display_notification(page)

		save_button = button.button('Save', on_save)
		doc_title = '<a href="/{0}/{1}" class="larch_app_doc_title">{2}</a>'.format(self.loc_prefix, doc.location, doc.name)
		doc_filename = '<span class="larch_app_doc_filename">{0}</span><span class="larch_app_doc_extension">.ularch</span>'.format(doc.filename)
		controls = Html('<div class="larch_app_doc_controls">', save_button, '</div>')
		return Html('<tr class="larch_app_doc">	<td>', doc_title, '</td><td>', doc_filename, '</td><td>', controls, '</td></tr>')




	def __present__(self, fragment):
		self.__incr.on_access()
		contents = ['<table class="larch_app_doc_list">']
		contents.append('<thead class="larch_app_doc_list_header"><td>Title</td><td>Filename</td><td>Save</td></thead>')
		contents.append('<tbody>')
		contents.extend([self.__doc_table_row(doc, fragment.page)   for doc in self.__documents])
		contents.append('</tbody></table>')
		return Html(*contents)





class ConsoleList (object):
	def __init__(self, app):
		self._app = app
		self.__consoles = []
		self.__incr = IncrementalValueMonitor()



	def __getitem__(self, item):
		return self.__consoles[item]

	def __len__(self):
		return len(self.__consoles)

	def new_console(self):
		con = console.PythonConsole()
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
			console_link = '<p class="larch_app_console"><a href="{0}/pages/consoles/{1}">Console {1}</a></p>'.format(self._app.app_location, i)
			contents.append( console_link)
		contents.append('</div>')
		return Html(*contents)





class Tool (object):
	def __init__(self):
		self._tool_list = None


	def close(self):
		self._tool_list.close(self)



class DocNameInUseTool (Tool):
	def __init__(self, filename):
		super(DocNameInUseTool, self).__init__()
		self.filename = filename

	def __present__(self, fragment):
		return Html('<div class="larch_app_doc_name_in_use"><p class="error_text">There is already a document in a file named \'{0}<em>.ularch</em>\'.</p>'.format(self.filename),
			    button.button('Close', lambda event: self.close), '</div>')


class NewDocumentTool (Tool):
	def __init__(self, doc_list, document_factory, initial_name):
		super(NewDocumentTool, self).__init__()
		self.__doc_list = doc_list
		self.__document_factory = document_factory
		self.__name = LiveValue(initial_name)


	def __present__(self, fragment):
		def on_edit(text):
			self.__name = text

		def on_create(event):
			filename = _sanitise_filename(self.__name.static_value)
			if self.__doc_list.doc_for_filename(filename) is not None:
				self._tool_list.add(DocNameInUseTool(filename))
			else:
				document = self.__document_factory()
				self.__doc_list.new_document_for_content(self.__name.static_value, document)
			self.close()

		def on_cancel(event):
			self.close()

		return Html('<div class="tool_box">',
				'<span class="gui_section_1">Create document</span><br>',
				'<table>',
				'<tr><td><span class="gui_label">Name:</span></td><td>', text_entry.live_text_entry(self.__name, width="40em"), '</td></tr>',
				'<tr><td>', button.button('Cancel', on_cancel), '</td><td>', button.button('Create', on_create), '</td></tr>',
				'</table>',
				'</div>')


class UploadIPynbTool (Tool):
	def __init__(self, doc_list):
		super(UploadIPynbTool, self).__init__()
		self.__doc_list = doc_list


	def __present__(self, fragment):
		def _on_upload(event, form_data):
			f = form_data.get('file')
			if f is not None:
				notebooks, notebook_name = ipynb_filter.load(f.file)

				filename = _sanitise_filename(notebook_name)
				filename = self.__doc_list.unused_filename(filename)
				self.__doc_list.new_document_for_content(filename, notebooks[0])
			self.close()

		def on_cancel(event):
			self.close()


		upload_form_contents = Html('<div><input type="file" name="file" size="50"/></div>',
					    '<table>',
					    '<tr><td>', button.button('Cancel', on_cancel), '</td><td>', form.submit_button('Upload'), '</td></tr>',
					    '</table>')
		upload_form = form.form(upload_form_contents, _on_upload)

		warning = ipynb_filter.markdown_warning()

		return Html('<div class="tool_box">',
				'<span class="gui_section_1">Upload IPython Noteook</span><br>',
				upload_form,
				warning   if warning is not None   else '',
				'</div>')



class DownloadIPynbFromWebTool (Tool):
	def __init__(self, doc_list):
		super(DownloadIPynbFromWebTool, self).__init__()
		self.__doc_list = doc_list
		self.__url = LiveValue('')



	def __present__(self, fragment):
		def on_edit(text):
			self.__url = text

		def on_import(event):
			url = self.__url.static_value
			url_l = url.lower()
			if not url_l.startswith('http://')  and  not url_l.startswith('https://'):
				url = 'http://' + url
			request = urllib2.Request(self.__url)
			request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13')
			opener = urllib2.build_opener()
			fp = opener.open(request)

			notebooks, notebook_name = ipynb_filter.load(fp)

			filename = _sanitise_filename(notebook_name)
			filename = self.__doc_list.unused_filename(filename)
			self.__doc_list.new_document_for_content(filename, notebooks[0])

			self.close()

		def on_cancel(event):
			self.close()

		warning = ipynb_filter.markdown_warning()

		return Html('<div class="tool_box">',
				'<span class="gui_section_1">Download IPython notebook from the web</span><br>',
				'<div><span class="gui_label">Web address (Github/Bitbucket RAW, etc):</span></div>',
				'<div><span>', text_entry.live_text_entry(self.__url, width="40em"), '</span></div>',
				'<table>',
				'<tr><td>', button.button('Cancel', on_cancel), '</td><td>', button.button('Import', on_import), '</td></tr>',
				'</table>',
				warning   if warning is not None   else '',
				'</div>')



class ToolList (object):
	def __init__(self):
		self.contents = []
		self.__incr = IncrementalValueMonitor()


	def add(self, box):
		box._tool_list = self
		self.contents.append(box)
		self.__incr.on_changed()


	def close(self, box):
		self.contents.remove(box)
		self.__incr.on_changed()


	def __present__(self, fragment):
		self.__incr.on_access()
		return Html(*self.contents)




class LarchApplication (object):
	def __init__(self, app_location, user_docs_path=None, documentation_path=None, logout_url_path=None):
		self.__path_to_document = {}
		self.__app_location = app_location

		if user_docs_path is None:
			user_docs_path = os.getcwd()
		if documentation_path is None:
			documentation_path = os.path.join(os.getcwd(), 'docs')
			if not os.path.exists(documentation_path):
				documentation_path = None

		self.__user_docs_path = user_docs_path
		self.__logout_url_path = logout_url_path

		self.__user_docs = DocumentList(self, user_docs_path, 'files')
		self.__user_docs.enable_import_hooks()

		if documentation_path is not None:
			self.__docs = DocumentList(self, documentation_path, 'docs')
			self.__docs.enable_import_hooks()
		else:
			self.__docs = None

		self.__consoles = ConsoleList(self)

		self.__tools = ToolList()


	@property
	def app_location(self):
		return self.__app_location

	@property
	def user_docs(self):
		return self.__user_docs

	@property
	def consoles(self):
		return self.__consoles


	def _get_document_for_path(self, path):
		a = os.path.abspath(path)
		return self.__path_to_document.get(a)

	def _set_document_for_path(self, path, doc):
		a = os.path.abspath(path)
		self.__path_to_document[a] = doc




	def __resolve__(self, name, subject):
		if name == 'files':
			subject.add_step(focus=self.__user_docs, location_trail=[name])
			return self.__user_docs
		elif name == 'docs'  and  self.__docs is not None:
			subject.add_step(focus=self.__docs, location_trail=[name])
			return self.__docs
		elif name == 'consoles':
			subject.add_step(focus=self.__consoles, location_trail=[name])
			return self.__consoles
		else:
			return None


	def __resolve_self__(self, subject):
		doc_url = '/docs/index'   if self.__docs is not None   else None
		subject.add_step(title='The Ubiquitous Larch', augment_page=_make_apply_page_frame(self.__logout_url_path, doc_url))
		return self


	def __present__(self, fragment):
		def _on_reload(event):
			self.__user_docs.reload()
			if self.__docs is not None:
				self.__docs.reload()


		reset_button = button.button('Reload', _on_reload)
		reset_section = Html('<div>', reset_button, '</div>')

		add_notebook = menu.item('Notebook', lambda event: self.__tools.add(NewDocumentTool(self.__user_docs, lambda: notebook.Notebook(), 'Notebook')))
		add_project = menu.item('Project', lambda event: self.__tools.add(NewDocumentTool(self.__user_docs, lambda: project_root.ProjectRoot(), 'Project')))
		new_item = menu.sub_menu('New', [add_notebook, add_project])
		new_document_menu = menu.menu([new_item], drop_down=True)


		upload_ipynb = menu.item('Upload', lambda event: self.__tools.add(UploadIPynbTool(self.__user_docs)))
		web_ipynb = menu.item('Download from web', lambda event: self.__tools.add(DownloadIPynbFromWebTool(self.__user_docs)))
		import_ipynb_item = menu.sub_menu('Import IPython notebook', [upload_ipynb, web_ipynb])
		import_ipynb_menu = menu.menu([import_ipynb_item], drop_down=True)


		document_controls = Html('<table class="larch_app_controls_row"><tr><td class="larch_app_control">', new_document_menu, '</td>',
					 '<td class="larch_app_control">', import_ipynb_menu, '</td></tr></table>')


		def on_new_console(event):
			self.__consoles.new_console()


		new_console_button = button.button('New console', on_new_console)


		contents = ["""
			<div class="larch_app_title_bar">The Ubiquitous Larch</div>

			<div class="larch_app_enclosure">
				<section class="larch_app_docs_section">
				<h2>Open documents:</h2>
			""",
			reset_section,
			self.__user_docs,
			document_controls,
			self.__tools,
			"""</section>
			<section class="larch_app_consoles_section">
				<h2>Consoles:</h2>
			""",
			self.__consoles,
			new_console_button,
			"""
			</section>
			<p class="larch_app_powered_by">The Ubiquitous Larch &copy; copyright Geoffrey French<br/>
			Powered by
			<a class="larch_app_pwr_link" href="http://www.python.org">Python</a>,
			<a class="larch_app_pwr_link" href="http://flask.pocoo.org">Flask</a>/<a class="larch_app_pwr_link" href="http://bottlepy.org">Bottle</a>/<a class="larch_app_pwr_link" href="http://www.cherrypy.org/">CherryPy</a>/<a class="larch_app_pwr_link" href="http://www.djangoproject.com/">Django</a>,
			<a class="larch_app_pwr_link" href="http://jquery.com/">jQuery</a>,
			<a class="larch_app_pwr_link" href="http://www.json.org/js.html">json.js</a>,
			<a class="larch_app_pwr_link" href="http://codemirror.net/">Code Mirror</a>,
			<a class="larch_app_pwr_link" href="http://ckeditor.com/">ckEditor</a>,
			<a class="larch_app_pwr_link" href="http://d3js.org/">d3.js</a>,
			<a class="larch_app_pwr_link" href="http://imakewebthings.com/deck.js/">deck.js</a> and
			<a class="larch_app_pwr_link" href="http://needim.github.io/noty/">noty</a></p>
			</div>
			"""]
		return Html(*contents).use_css(url=larch_app_css)







def create_service(app_location, options=None, documentation_path=None, logout_url_path=None):
	docpath = options.docpath   if options is not None   else None
	app = LarchApplication(app_location, docpath, documentation_path, logout_url_path)

	return ProjectionService(app)



def parse_cmd_line():
	parser = OptionParser()
	parser.add_option('-p', '--port', dest='port', help='server port', type='int', default=5000)
	parser.add_option('-d', '--docpath', dest='docpath', help='Documents path', default=None)

	options, args = parser.parse_args()
	return options