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
import json
from optparse import OptionParser
from larch.apps.notebook import ipynb_filter
from larch.apps.project import project_root
from larch.apps.notebook import notebook

from larch.core.projection_service import ProjectionService
from larch.incremental import IncrementalValueMonitor
from larch import command
from larch.apps.console import console
from larch.controls import form, button, menu, text_entry, noty, file_chooser
from larch.live import LiveValue
from larch.pres.pres import Pres, CompositePres
from larch.pres.html import Html
from larch.pres import resource


_EXTENSION = '.ularch'



class DocumentNameInUseError (object):
	pass




larch_app_css = '/static/larch/larch_app.css'





_filename_chars = string.ascii_letters + string.digits + ' _-.'

def _sanitise_filename_char(x):
	return x   if x in _filename_chars   else '_'

def _sanitise_filename(name):
	return ''.join([_sanitise_filename_char(x)  for x in name])




class LarchAppContext (object):
	def __init__(self, logout_url_path, documentation_url):
		self.logout_url_path = logout_url_path
		self.documentation_url = documentation_url








#
#
# FRAGMENT INSPECTOR
#
#

def _inspector_entry(fragment):
	model = fragment.model

	destination = console.PythonConsole()
	destination.add_binding('m', model)

	model_is_presentable = isinstance(model, Pres)
	model_type_css_class = 'inspector_model_pres'   if model_is_presentable   else 'inspector_model_python'
	model_type_descr = ' (presentation type)'   if model_is_presentable   else ' (a Python object)'
	model_descr = Html('<span class="{0}">{1}</span>{2}<br><span class="inspector_id">id: {3}</span>'.format(model_type_css_class, type(model).__name__, model_type_descr, id(model)))

	rsc = resource.PresLink(destination, model_descr)
	anchor = rsc.js_function_call('larch.controls.initInspectorEntry', fragment.segment_id)
	return Html('<li>', anchor, '</li>')


def invoke_inspector(event, fragment):
	# Build a list of fragments above it
	fragments = []
	while fragment is not None:
		if fragment.is_inspector_enabled():
			fragments.append(fragment)
		fragment = fragment.parent


	entries = [_inspector_entry(f)   for f in fragments]
	content = Html('<ul class="fragment_inspector_list">').extend(entries).append('</ul>')
	noty.noty(content, layout='bottom').show_on(event)











#
#
# PAGE FRAME
#
#


class PageFrame (CompositePres):
	def __init__(self, subject, app_context):
		self.__page = subject.focus
		self.__focii = subject.focii
		self.__app_context = app_context



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
		if self.__app_context.documentation_url is not None:
			doc_link = Html('<a class="__larch_app_doc_link" href="{0}">Documentation</a>'.format(self.__app_context.documentation_url))
			right_menu_bar_contents.append(doc_link)

		# Command bar button
		cmd_bar_button = Html('<button class="__larch_app_cmd_bar_button">Cmd. bar (Esc)</button>').js_function_call("larch.controls.initToggleCommandBarButton")
		right_menu_bar_contents.append(cmd_bar_button)

		# Logout link
		if self.__app_context.logout_url_path is not None:
			#right_menu_bar_contents.append(Html('<div class="__larch_app_frame_logout_link"><a href="{0}">Logout</a></div>'.format(self.__logout_url_path)))
			right_menu_bar_contents.append(Html('<a href="{0}">Logout</a>'.format(self.__app_context.logout_url_path)).js_eval('$(node).button();'))

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
			menu_bar_contents.extend(method(fragment.page, fragment))

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



def _make_apply_page_frame(app_context):
	def _apply_page_frame(subject):
		return PageFrame(subject, app_context)
	return _apply_page_frame



def name_to_location(name):
	return ''.join([x   for x in name   if x in string.ascii_letters + string.digits + '_'])

def path_to_name(path):
	filename = os.path.split(path)[1]
	return os.path.splitext(filename)

def path_to_location(path):
	return name_to_location(path_to_name(path))




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





#
#
# IMPORT HOOK HELPERS
#
#


import traceback

class _ImportHookFinderWrapper (object):
	def __init__(self, kernel,  finder):
		self.__kernel = kernel
		self.__finder = finder

	def load_module(self, fullname):
		try:
			return self.__finder.__load_module__(self.__kernel, fullname)
		except:
			traceback.print_exc()
			raise




class _DocKernelImportHooks (object):
	def __init__(self, doc_kernel):
		self.__doc_kernel = doc_kernel


	def find_module(self, fullname, path=None):
		try:
			finder = self.__doc_kernel.find_module(fullname, path)
			if finder is not None:
				return _ImportHookFinderWrapper(self.__doc_kernel, finder)
			return None
		except:
			traceback.print_exc()
			raise



#
#
# DOCUMENT KERNEL
#
#

class DocumentKernel (object):
	def __init__(self, path, name, content, app_context, imported_module_registry=None):
		if imported_module_registry is None:
			imported_module_registry = ImportedModuleRegistry()
		self.__imported_module_registry = imported_module_registry
		self.__app_context = app_context

		self.__path = path
		self.__name = name
		self.__content = content
		self.__document_modules = {}

		self.__import_hooks = _DocKernelImportHooks(self)
		self.enable_import_hooks()



	def kernel_message(self, message, *args, **kwargs):
		if message == 'save':
			self.save()
		else:
			raise ValueError, 'Unreckognised message {0}'.format(message)


	def enable_import_hooks(self):
		if self.__import_hooks not in sys.meta_path:
			sys.meta_path.append(self.__import_hooks)



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



	def __commands__(self, page):
		return [
			command.Command([command.Key(ord('S'))], 'Save', self.__on_save_command),
			command.Command([command.Key(ord('U'))], 'Unload modules', self.__on_unload_modules_command),
		]


	def __resolve_self__(self, subject):
		subject.add_step(document=self, focus=self.__content, title=self.__name, augment_page=_make_apply_page_frame(self.__app_context), invoke_inspector=invoke_inspector)
		return self.__content



	def save(self):
		# Convert to string first, in case we encounter an exception while pickling
		# This way, the save process bails *before* overwriting the file with nonsense
		s = pickle.dumps(self.__content)
		with open(self.__path, 'w') as f:
			f.write(s)
		return os.path.split(self.__path)[1]


	@staticmethod
	def load(path, name, app_context, imported_module_registry):
		try:
			with open(path, 'rU') as f:
				content = pickle.load(f)
		except:
			print 'Error: could not load {0}: {1}'.format(path, sys.exc_info())
		else:
			return DocumentKernel(path, name, content, app_context, imported_module_registry)



def make_kernel_service_for_content_factory(kernel_interface, path, name, content_factory, app_context, imported_module_registry):
	content = content_factory()
	kernel = DocumentKernel(path, name, content, app_context, imported_module_registry)
	service = ProjectionService(kernel)
	return service

def make_kernel_service_from_file(kernel_interface, path, name, app_context, imported_module_registry):
	kernel = DocumentKernel.load(path, name, app_context, imported_module_registry)
	service = ProjectionService(kernel)
	return service






#
#
# DOCUMENT
#
#

class Document (object):
	def __init__(self, doc_list, name, filename, location):
		self.__doc_list = doc_list
		self.__name = name
		self.__filename = filename
		self.__loc = location



	@property
	def name(self):
		return self.__name

	@property
	def filename(self):
		return self.__filename

	@property
	def location(self):
		return self.__loc



	def save(self):
		print 'SENDING SAVE MESSAGE TO {0}/{1}'.format(self.__doc_list.category, self.__loc)
		self.__doc_list._app.kernel_interface.kernel_message(self.__doc_list.category, self.__loc, 'save')
		return self.__filename


	@staticmethod
	def load(on_doc_loaded, app, doc_list, path, app_context, imported_module_registry):
		"""
		Load a document (uses continuation passing style instead of a return value)

		:param on_doc_loaded: a callback of the form function(doc) that us invoked when the document has been loaded; this is invoked instead of a returning a value, in order to permit asynchronous operation
		:param app: the larch application
		:param doc_list: the document list
		:param path: the path at which the document file can be found
		:param app_context: a LarchAppContext
		:param imported_module_registry: module registry for handling imported modules
		"""
		filename = os.path.split(path)[1]
		name = os.path.splitext(filename)[0]
		location = name_to_location(name)

		doc = app._get_document_for_path(path)
		if doc is None:

			def on_created():
				doc = Document(doc_list, name, name, location)
				app._set_document_for_path(path, doc)
				on_doc_loaded(doc)

			app.kernel_interface.new_kernel(on_created, doc_list.category, location, make_kernel_service_from_file, path, name, app_context, imported_module_registry)
		else:
			def on_aliased():
				on_doc_loaded(doc)
			app.kernel_interface.alias_category_and_name(on_aliased, doc_list.category, location, doc.__doc_list.category, doc.__loc)


	@staticmethod
	def for_content(on_doc_created, doc_list, name, filename, path, content_factory, app_context, imported_module_registry):
		"""
		Create a new document (uses continuation passing style instead of a return value)

		:param on_doc_created: a callback of the form function(doc) that us invoked when the document has been created; this is invoked instead of a returning a value, in order to permit asynchronous operation
		:param doc_list: the document list
		:param name: the name for the new document
		:param filename: the filename for the new document
		:param path: the path to the file in which the new document is to be saved
		:param content_factory: a callback of the form function() that creates the content of the document
		:param app_context: a LarchAppContext
		:param imported_module_registry: module registry for handling imported modules
		"""
		location = name_to_location(name)

		def on_created():
			doc = Document(doc_list, name, filename, location)
			on_doc_created(doc)

		doc_list._app.kernel_interface.new_kernel(on_created, doc_list.category, location, make_kernel_service_for_content_factory, path, name, content_factory, app_context, imported_module_registry)








class DocumentList (object):
	def __init__(self, app, category, path, loc_prefix, app_context, on_docs_loaded):
		self.__incr = IncrementalValueMonitor()

		self.category = category
		self.__app_context = app_context

		self.__imported_module_registry = ImportedModuleRegistry()

		self._app = app
		self.__path = path
		self.__loc_prefix = loc_prefix

		self.__documents = []
		self.__docs_by_location = {}
		self.__docs_by_filename = {}

		self.__load_documents(on_docs_loaded)



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

	def new_document_for_content(self, name, content_factory):
		if name in self.__docs_by_filename:
			raise DocumentNameInUseError, name
		# Document file names do NOT include the extension
		filename = _sanitise_filename(name)
		file_path = os.path.join(self.__path, filename + '.ularch')

		def on_doc_created(doc):
			doc.save()
			self.__add_document(doc)

		Document.for_content(on_doc_created, self, name, filename, file_path, content_factory, self.__app_context, self.__imported_module_registry)


	def reload(self):
		self.__documents = []
		self.__docs_by_location = {}
		self.__docs_by_filename = {}

		self.__load_documents(None)

		self.__incr.on_changed()



	def __load_documents(self, on_all_docs_loaded):
		file_paths = glob.glob(os.path.join(self.__path, '*' + _EXTENSION))
		num_docs_to_load = len(file_paths)
		docs_loaded = [0]

		def on_doc_loaded(doc):
			self.__add_document(doc)
			docs_loaded[0] += 1
			if docs_loaded[0] == num_docs_to_load  and  on_all_docs_loaded is not None:
				on_all_docs_loaded()

		for p in sorted(file_paths):
			Document.load(on_doc_loaded, self._app, self, p, self.__app_context, self.__imported_module_registry)




	def __doc_table_row(self, doc, page):
		def on_save(event):
			doc.save_and_display_notification(page)

		save_button = button.button('Save', on_save)
		doc_title = '<a href="/pages/{0}/{1}" class="larch_app_doc_title">{2}</a>'.format(self.loc_prefix, doc.location, doc.name)
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
				self.__doc_list.new_document_for_content(self.__name.static_value, self.__document_factory)
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



class _IPynbContentFactory (object):
	def __init__(self, ipynb_json):
		self.__ipynb_json = ipynb_json


	def __call__(self):
		notebooks, notebook_name = ipynb_filter.convert_ipynb_json(self.__ipynb_json)
		return notebooks[0]


	@staticmethod
	def load(f):
		ipynb_json = json.load(f)
		name = ipynb_filter.get_name_from_ipynb_json(ipynb_json)
		factory = _IPynbContentFactory(ipynb_json)
		return name, factory

	@staticmethod
	def loads(s):
		ipynb_json = json.loads(s)
		name = ipynb_filter.get_name_from_ipynb_json(ipynb_json)
		factory = _IPynbContentFactory(ipynb_json)
		return name, factory



class UploadIPynbTool (Tool):
	def __init__(self, doc_list):
		super(UploadIPynbTool, self).__init__()
		self.__doc_list = doc_list


	def __present__(self, fragment):
		def _on_upload(event, file_name, fp):
			notebook_name, factory = _IPynbContentFactory.load(fp)

			filename = _sanitise_filename(notebook_name)
			filename = self.__doc_list.unused_filename(filename)
			self.__doc_list.new_document_for_content(filename, factory)
			self.close()

		def on_cancel(event):
			self.close()


		chooser = file_chooser.upload_file_chooser(_on_upload, on_cancel)



		warning = ipynb_filter.markdown_warning()

		return Html('<div class="tool_box">',
				'<span class="gui_section_1">Upload IPython Noteook</span><br>',
				chooser,
				warning   if warning is not None   else '',
				'</div>')



class DownloadIPynbFromWebTool (Tool):
	def __init__(self, doc_list):
		super(DownloadIPynbFromWebTool, self).__init__()
		self.__doc_list = doc_list
		self.__url = LiveValue('')



	def __present__(self, fragment):
		def on_downloaded(event, file_name, fp):
			notebook_name, factory = _IPynbContentFactory.load(fp)

			filename = _sanitise_filename(notebook_name)
			filename = self.__doc_list.unused_filename(filename)
			self.__doc_list.new_document_for_content(filename, factory)

			self.close()

		def on_cancel(event):
			self.close()

		chooser = file_chooser.fetch_from_web_file_chooser(on_downloaded, on_cancel)

		warning = ipynb_filter.markdown_warning()

		return Html('<div class="tool_box">',
				'<span class="gui_section_1">Download IPython notebook from the web (GitHub, Bitbucket RAW, etc.)</span><br>',
				chooser,
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
	def __init__(self, kernel_interface, app_location, user_docs_path=None, documentation_path=None, logout_url_path=None):
		self.__path_to_document = {}
		self.__app_location = '/pages' + app_location

		self.kernel_interface = kernel_interface

		if user_docs_path is None:
			user_docs_path = os.getcwd()
		if documentation_path is None:
			documentation_path = os.path.join(os.getcwd(), 'docs')
			if not os.path.exists(documentation_path):
				documentation_path = None

		self.__app_context = LarchAppContext(logout_url_path, '/pages/docs/index'   if documentation_path is not None   else None)


		self.__user_docs_path = user_docs_path
		self.__logout_url_path = logout_url_path

		def on_user_docs_loaded():
			if documentation_path is not None:
				self.__docs = DocumentList(self, 'docs', documentation_path, 'docs', self.__app_context, None)
			else:
				self.__docs = None

		self.__user_docs = DocumentList(self, 'files', user_docs_path, 'files', self.__app_context, on_user_docs_loaded)


		self.__tools = ToolList()



	@property
	def app_location(self):
		return self.__app_location

	@property
	def user_docs(self):
		return self.__user_docs


	def _get_document_for_path(self, path):
		a = os.path.abspath(path)
		return self.__path_to_document.get(a)

	def _set_document_for_path(self, path, doc):
		a = os.path.abspath(path)
		self.__path_to_document[a] = doc




	def kernel_message(self, message, *args, **kwargs):
		raise ValueError, 'Unreckognised message {0}'.format(message)




	def __resolve_self__(self, subject):
		subject.add_step(title='The Ubiquitous Larch', augment_page=_make_apply_page_frame(self.__app_context), invoke_inspector=invoke_inspector)
		return self


	def __present__(self, fragment):
		def _on_reload(event):
			self.__user_docs.reload()
			if self.__docs is not None:
				self.__docs.reload()


		reset_button = button.button('Reload', _on_reload)
		reset_section = Html('<div>', reset_button, '</div>')

		add_notebook = menu.item('Notebook', lambda event: self.__tools.add(NewDocumentTool(self.__user_docs, notebook.Notebook, 'Notebook')))
		add_project = menu.item('Project', lambda event: self.__tools.add(NewDocumentTool(self.__user_docs, project_root.ProjectRoot, 'Project')))
		new_item = menu.sub_menu('New', [add_notebook, add_project])
		new_document_menu = menu.menu([new_item], drop_down=True)


		upload_ipynb = menu.item('Upload', lambda event: self.__tools.add(UploadIPynbTool(self.__user_docs)))
		web_ipynb = menu.item('Download from web', lambda event: self.__tools.add(DownloadIPynbFromWebTool(self.__user_docs)))
		import_ipynb_item = menu.sub_menu('Import IPython notebook', [upload_ipynb, web_ipynb])
		import_ipynb_menu = menu.menu([import_ipynb_item], drop_down=True)


		document_controls = Html('<table class="larch_app_controls_row"><tr><td class="larch_app_control">', new_document_menu, '</td>',
					 '<td class="larch_app_control">', import_ipynb_menu, '</td></tr></table>')


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
			<section>
			<p>For more information on using the Ubiquitous Larch, please see the <a href="/pages/docs/index">documentation</a>.</p>
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







def create_service(kernel_interface, app_location, options=None, args=[], documentation_path=None, logout_url_path=None):
	docpath = args[0]   if len(args) > 0   else None
	app = LarchApplication(kernel_interface, app_location, docpath, documentation_path, logout_url_path)

	return ProjectionService(app)



def parse_cmd_line():
	usage = "usage: %prog [options] <documents_path>"
	parser = OptionParser(usage)
	parser.add_option('-p', '--port', dest='port', help='server port', type='int', default=5000)

	return parser.parse_args()