##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import json
import os

import mimetypes

from britefury.dynamicsegments.segment import HtmlContent
from britefury.pres.pres import Resource

__author__ = 'Geoff'





class JsonResource (Resource):
	def __init__(self, data_fn):
		super(JsonResource, self).__init__(lambda: json.dumps(data_fn()), 'application/json')



class CSVResource (Resource):
	def __init__(self, data_fn):
		super(CSVResource, self).__init__(data_fn, 'text/csv')



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

