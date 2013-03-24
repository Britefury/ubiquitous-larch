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

sample_code = """
from britefury.pres.pres import *
from britefury.pres.resource import *
from britefury.pres.html import Html

js_url = '/lightbox/js/lightbox.js'
css_url = '/lightbox/css/lightbox.css'

def lightbox(urls, groupname):
	images = ''.join(['<a href="{0}" rel="lightbox[{1}]"><img src="{0}" width="128" height="96"></a>'.format(url, groupname)   for url in urls])
	return Html(images).use_js(js_url).use_css(css_url)

url1 = 'http://www.cutedecision.com/wp-content/uploads/2011/06/PaigeBradleyExpansion2_1.jpg'
url2 = 'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQW9yKl7zviaEN0dsbF1eX5kDJGVhNb-zCuOViKGc4lGa6PgCRgtA'

lightbox([url1, url2], 'test')

"""


def create_service():
	#focus = console.Console(sample_code)
	focus = worksheet.Worksheet()
	index_subject = Subject(None, focus, title='Test')


	return DynamicDocumentService(lambda dynamic_document: IncrementalView(index_subject, dynamic_document))
