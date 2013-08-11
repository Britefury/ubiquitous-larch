##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json
import os

import mimetypes

from larch.core.dynamicpage.segment import HtmlContent
from larch.live import LiveFunction
from larch.pres import pres, js
from larch.core.subject import Subject




class Resource (pres.Pres, js.JS):
	def page_ref(self, pres_ctx, change_listener, url):
		pass

	def page_unref(self, pres_ctx, change_listener):
		pass


	def build(self, pres_ctx):
		return HtmlContent([])

	def build_js(self, pres_ctx):
		instance = self._get_instance(pres_ctx)
		return instance.client_side_js()

	def _get_instance(self, pres_ctx):
		return pres_ctx.fragment_view.get_resource_instance(self, pres_ctx)




class URLResource (Resource):
	def get_data(self):
		raise NotImplementedError, 'abstract'

	def get_mime_type(self):
		raise NotImplementedError, 'abstract'

	def build(self, pres_ctx):
		return HtmlContent([self._url(pres_ctx)])

	def _url(self, pres_ctx):
		rsc_instance = pres_ctx.fragment_view.get_resource_instance(self, pres_ctx)
		return rsc_instance.url







class ConstResource (URLResource):
	def __init__(self, data, mime_type):
		super(ConstResource, self).__init__()
		self.__data = data
		self.__mime_type = mime_type


	def get_data(self):
		return self.__data

	def get_mime_type(self):
		return self.__mime_type



class JsonResource (ConstResource):
	def __init__(self, data):
		super(JsonResource, self).__init__(json.dumps(data), 'application/json')



class CSVResource (ConstResource):
	def __init__(self, data):
		super(CSVResource, self).__init__(data, 'text/csv')



class FnResource (URLResource):
	def __init__(self, data_fn, mime_type):
		super(FnResource, self).__init__()
		self.__data_fn = data_fn
		self.__mime_type = mime_type


	def get_data(self):
		return self.__data_fn()

	def get_mime_type(self):
		return self.__mime_type





class JsonFnResource (FnResource):
	def __init__(self, data_fn):
		super(JsonFnResource, self).__init__(lambda: json.dumps(data_fn()), 'application/json')



class CSVFnResource (FnResource):
	def __init__(self, data_fn):
		super(CSVFnResource, self).__init__(data_fn(), 'text/csv')





class LiveFnResource (URLResource):
	def __init__(self, data_fn, mime_type):
		self.__data_fn = LiveFunction(data_fn)
		self.__mime_type = mime_type
		self.__change_listeners = []
		self.__ref_count = 0

	def page_ref(self, pres_ctx, change_listener, url):
		self.__change_listeners.append(change_listener)
		if self.__ref_count == 0:
			self.__data_fn.add_listener(self.__live_listener)
		self.__ref_count += 1


	def page_unref(self, pres_ctx, change_listener):
		self.__ref_count -= 1
		if self.__ref_count == 0:
			self.__data_fn.remove_listener(self.__live_listener)
		self.__change_listeners.remove(change_listener)


	def __live_listener(self, incr):
		for listener in self.__change_listeners:
			listener()


	def get_data(self):
		return self.__data_fn()

	def get_mime_type(self):
		return self.__mime_type



class JsonLiveFnResource (LiveFnResource):
	def __init__(self, data_fn):
		super(JsonLiveFnResource, self).__init__(lambda: json.dumps(data_fn()), 'application/json')



class CSVLiveFnResource (LiveFnResource):
	def __init__(self, data_fn):
		super(CSVLiveFnResource, self).__init__(data_fn, 'text/csv')





class ImageFromFile (URLResource):
	def __init__(self, filename, width=None, height=None):
		super(ImageFromFile, self).__init__()
		self.__filename = filename
		self.__width = width
		self.__height = height
		self.__data = None
		self.__mime_type = ''



	def get_data(self):
		if self.__data is None:
			if os.path.exists(self.__filename)  and  os.path.isfile(self.__filename):
				f = open(self.__filename, 'rb')
				self.__data = f.read()
				self.__mime_type = mimetypes.guess_type(self.__filename)[0]
				f.close()
		return self.__data

	def get_mime_type(self):
		return self.__mime_type


	def build(self, pres_ctx):
		url = self._url(pres_ctx)
		w = ' width="{0}"'.format(self.__width)   if self.__width is not None   else ''
		h = ' height="{0}"'.format(self.__height)   if self.__height is not None   else ''
		return HtmlContent(['<img src="', url, '"{0}{1}>'.format(w, h)])




class ImageFromBinary (ConstResource):
	def __init__(self, data, mime_type, width=None, height=None):
		super(ImageFromBinary, self).__init__(data, mime_type)
		self.__width = width
		self.__height = height



	def build(self, pres_ctx):
		url = self._url(pres_ctx)
		w = ' width="{0}"'.format(self.__width)   if self.__width is not None   else ''
		h = ' height="{0}"'.format(self.__height)   if self.__height is not None   else ''
		return HtmlContent(['<img src="', url, '"{0}{1}>'.format(w, h)])




class SubjectResource (URLResource):
	def __init__(self, subject):
		super(SubjectResource, self).__init__()
		self.__subject = subject
		self.__data = None
		self.__mime_type = ''


	def page_ref(self, pres_ctx, change_listener, url):
		if self.__data is None:
			self.__data = pres_ctx.fragment_view.service.page_for_subject(self.__subject, url.strip('/'))
			self.__mime_type = 'text/html'


	def get_data(self):
		return self.__data

	def get_mime_type(self):
		return self.__mime_type




class PresResource (URLResource):
	def __init__(self, contents):
		super(PresResource, self).__init__()
		self.__contents = contents
		self.__data = None
		self.__mime_type = ''


	def page_ref(self, pres_ctx, change_listener, url):
		subj = Subject()
		subj.add_step(focus=self.__contents, perspective=pres_ctx.perspective, title='Resource')
		self.__data = pres_ctx.fragment_view.service.page_for_subject(subj, url.strip('/'))
		self.__mime_type = 'text/html'


	def get_data(self):
		return self.__data

	def get_mime_type(self):
		return self.__mime_type





class SubjectIFrame (SubjectResource):
	def __init__(self, subject, width, height):
		super(SubjectIFrame, self).__init__(subject)
		self.__width = width
		self.__height = height



	def build(self, pres_ctx):
		url = self._url(pres_ctx)
		w = ' width="{0}"'.format(self.__width)   if self.__width is not None   else ''
		h = ' height="{0}"'.format(self.__height)   if self.__height is not None   else ''
		return HtmlContent(['<iframe src="', url, '"{0}{1}></iframe>'.format(w, h)])



class PresIFrame (PresResource):
	def __init__(self, subject, width, height):
		super(PresIFrame, self).__init__(subject)
		self.__width = width
		self.__height = height



	def build(self, pres_ctx):
		url = self._url(pres_ctx)
		w = ' width="{0}"'.format(self.__width)   if self.__width is not None   else ''
		h = ' height="{0}"'.format(self.__height)   if self.__height is not None   else ''
		return HtmlContent(['<iframe src="', url, '"{0}{1}></iframe>'.format(w, h)])


