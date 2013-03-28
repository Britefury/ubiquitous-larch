##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json
import os

import mimetypes

from britefury.dynamicsegments.segment import HtmlContent
from britefury.pres.pres import Resource
from britefury.projection.subject import Subject

__author__ = 'Geoff'




class ConstResource (Resource):
	class _ConstResourceData (object):
		def __init__(self, data, mime_type):
			self.data = data
			self.mime_type = mime_type

		def initialise(self, pres_ctx):
			pass

		def dispose(self, pres_ctx):
			self.data = None
			self.mime_type = None


class JsonResource (ConstResource):
	def __init__(self, data):
		super(JsonResource, self).__init__(self._ConstResourceData(json.dumps(data), 'application/json'))



class CSVResource (ConstResource):
	def __init__(self, data):
		super(CSVResource, self).__init__(self._ConstResourceData(data, 'application/json'))



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
			subj = Subject(None, self.__contents, pres_ctx.perspective)
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


