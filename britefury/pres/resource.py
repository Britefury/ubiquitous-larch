##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json
import os

import mimetypes

from britefury.dynamicsegments.segment import HtmlContent
from britefury.pres.pres import Resource
from britefury.live.live_function import LiveFunction
from britefury.projection.subject import Subject

__author__ = 'Geoff'




class ResourceData (object):
	def initialise(self, context, change_listener):
		raise NotImplementedError, 'abstract'

	def dispose(self, context):
		raise NotImplementedError, 'abstract'

	@property
	def data(self):
		raise NotImplementedError, 'abstract'

	@property
	def mime_type(self):
		raise NotImplementedError, 'abstract'




class ConstResource (Resource):
	class _ConstResourceData (ResourceData):
		def __init__(self, data, mime_type):
			self.data = data
			self.mime_type = mime_type

		def initialise(self, pres_ctx, change_listener):
			pass

		def dispose(self, pres_ctx):
			self.data = None
			self.mime_type = None


class JsonResource (ConstResource):
	def __init__(self, data):
		super(JsonResource, self).__init__(self._ConstResourceData(json.dumps(data), 'application/json'))



class CSVResource (ConstResource):
	def __init__(self, data):
		super(CSVResource, self).__init__(self._ConstResourceData(data, 'text/csv'))



class FnResource (Resource):
	class _FnResourceData (object):
		def __init__(self, data_fn, mime_type):
			self.data_fn = data_fn
			self.mime_type = mime_type

		def initialise(self, pres_ctx, change_listener):
			pass

		def dispose(self, pres_ctx):
			self.data_fn = None
			self.mime_type = None

		@property
		def data(self):
			return self.data_fn()


class JsonFnResource (FnResource):
	def __init__(self, data_fn):
		super(JsonFnResource, self).__init__(self._FnResourceData(lambda: json.dumps(data_fn()), 'application/json'))



class CSVFnResource (FnResource):
	def __init__(self, data_fn):
		super(CSVFnResource, self).__init__(self._FnResourceData(data_fn(), 'text/csv'))





class LiveFnResource (Resource):
	class _LiveFnResourceData (object):
		def __init__(self, data_fn, mime_type):
			self.data_fn = LiveFunction(data_fn)
			self.mime_type = mime_type
			self.__change_listener = None

		def initialise(self, pres_ctx, change_listener):
			self.__change_listener = change_listener
			self.data_fn.add_listener(self._live_listener)


		def dispose(self, pres_ctx):
			self.data_fn.remove_listener(self._live_listener)
			self.data_fn = None
			self.mime_type = None
			self.__change_listener = None


		def _live_listener(self, incr):
			self.__change_listener()

		@property
		def data(self):
			return self.data_fn()


class JsonLiveFnResource (LiveFnResource):
	def __init__(self, data_fn):
		super(JsonLiveFnResource, self).__init__(self._LiveFnResourceData(lambda: json.dumps(data_fn()), 'application/json'))



class CSVLiveFnResource (LiveFnResource):
	def __init__(self, data_fn):
		super(CSVLiveFnResource, self).__init__(self._LiveFnResourceData(data_fn(), 'text/csv'))





class ImageFromFile (Resource):
	class _ImageFromFileResourceData (object):
		def __init__(self, filename):
			self.__filename = filename
			self.data = ''
			self.mime_type = ''

		def initialise(self, pres_ctx):
			if os.path.exists(self.__filename)  and  os.path.isfile(self.__filename):
				f = open(self.__filename, 'rb')
				self.data = f.read()
				self.mime_type = mimetypes.guess_type(self.__filename)[0]
				f.close()

		def dispose(self, pres_ctx):
			self.data = None
			self.mime_type = None



	def __init__(self, filename, width=None, height=None):
		super(ImageFromFile, self).__init__(self._ImageFromFileResourceData(filename))
		self.__width = width
		self.__height = height



	def build(self, pres_ctx):
		url = self._url(pres_ctx)
		w = ' width="{0}"'.format(self.__width)   if self.__width is not None   else ''
		h = ' height="{0}"'.format(self.__height)   if self.__height is not None   else ''
		return HtmlContent(['<img src="', url, '"{0}{1}>'.format(w, h)])




class SubjectResource (Resource):
	class _SubjectResourceData (object):
		def __init__(self, subject):
			self.__subject = subject
			self.data = ''
			self.mime_type = ''


		def initialise(self, pres_ctx):
			self.data = pres_ctx.fragment_view.service.page(self.__subject)
			self.mime_type = 'text/html'

		def dispose(self, pres_ctx):
			self.data = ''
			self.mime_type = ''


	def __init__(self, subject):
		super(SubjectResource, self).__init__(self._SubjectResourceData(subject))



class PresResource (Resource):
	class _PresResourceData (object):
		def __init__(self, contents):
			self.__contents = contents
			self.data = ''
			self.mime_type = ''


		def initialise(self, pres_ctx):
			subj = Subject()
			subj.add_step(focus=self.__contents, perspective=pres_ctx.perspective, title='Resource')
			self.data = pres_ctx.fragment_view.service.page(subj)
			self.mime_type = 'text/html'

		def dispose(self, pres_ctx):
			self.data = ''
			self.mime_type = ''


	def __init__(self, subject):
		super(PresResource, self).__init__(self._PresResourceData(subject))



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


