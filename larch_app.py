##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os

from britefury.dynamicsegments.service import DynamicDocumentService

from britefury.projection.subject import Subject
from britefury.incremental_view.incremental_view import IncrementalView
from larch.console import console
from larch.worksheet import worksheet



sample_code = """
from britefury.pres.pres import *
from britefury.pres.resource import *
from britefury.pres.html import Html

filename='c:\\\\Users\\\\Geoff\\\\Pictures\\\\trollface.jpg'
f=open(filename,'rb')
data=f.read()
f.close()

r=Resource(lambda: data, 'image/jpeg')
Html('<img src="', r, '">')

ImageFromFile(filename)
"""


def create_service():
	#focus = console.Console(sample_code)
	focus = worksheet.Worksheet()
	index_subject = Subject(None, focus,
				stylesheet_names=[
					'codemirror/lib/codemirror.css',
					],
				script_names=[
					'ckeditor/ckeditor.js',
					'codemirror/lib/codemirror.js',
					'codemirror/mode/python/python.js',
					'controls.js',
					])


	return DynamicDocumentService(lambda dynamic_document: IncrementalView(index_subject, dynamic_document))
