##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json
import os

import mimetypes

from britefury.dynamicsegments.segment import HtmlContent
from britefury.pres.pres import Pres, CompositePres

__author__ = 'Geoff'


class Resource (Pres):
	def __init__(self, data_fn, mime_type):
		self.__data_fn = data_fn
		self.__mime_type = mime_type


	def build(self, pres_ctx):
		rsc = pres_ctx.fragment_view.create_resource(self.__data_fn, self.__mime_type)
		return HtmlContent([rsc.url])




class ImageFromFile (Resource):
	def __init__(self, filename, width=None, height=None):
		super(ImageFromFile, self).__init__(self.__read_data, mimetypes.guess_type(filename)[0])
		self.__data = None
		self.__filename = filename
		self.__width = width
		self.__height = height
		self.__read = False


	def __read_data(self):
		if not self.__read:
			if os.path.exists(self.__filename)  and  os.path.isfile(self.__filename):
				f = open(self.__filename, 'rb')
				self.__data = f.read()
				f.close()
			self.__read = True
		return self.__data


	def build(self, pres_ctx):
		url = super(ImageFromFile, self).build(pres_ctx)
		w = ' width="{0}'.format(self.__width)   if self.__width is not None   else ''
		h = ' height="{0}'.format(self.__height)   if self.__height is not None   else ''
		return HtmlContent(['<img src="', url, '"{0}{1}>'.format(w, h)])

