##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os
import cherrypy
from britefury.dynamicsegments.service import DynamicDocumentService

from britefury.projection.subject import Subject
from britefury.incremental_view.incremental_view import IncrementalView
from larch.console import console
from larch.worksheet import worksheet



config = {'/':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}


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
"""


#focus = console.Console(sample_code)
focus = worksheet.Worksheet()
index_subject = Subject(None, focus, stylesheet_names=['codemirror/lib/codemirror.css'], script_names=['codemirror/lib/codemirror.js', 'codemirror/mode/python/python.js', 'controls.js'])




class WebCombinatorServer (object):
	def __init__(self):
		self.service = DynamicDocumentService(self.__init_document)


	def __init_document(self, dynamic_document):
		return IncrementalView(index_subject, dynamic_document)


	def index(self):
		return self.service.index()

	index.exposed = True



	def event(self, session_id, event_data):
		return self.service.event(session_id, event_data)

	event.exposed = True


	def rsc(self, session_id, rsc_id):
		data, mime_type = self.service.resource(session_id, rsc_id)
		cherrypy.response.headers['Content-Type'] = mime_type
		return data

	rsc.exposed = True



root = WebCombinatorServer()
cherrypy.server.socket_port = 5000
cherrypy.quickstart(root, config=config)
