##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os

from bottle import Bottle, run, static_file, request, response

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

ImageFromFile(filename)
"""


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


app = Bottle()


service = DynamicDocumentService(lambda dynamic_document: IncrementalView(index_subject, dynamic_document))

@app.route('/')
def index():
	return service.index()


@app.route('/event', method='POST')
def event():
	session_id = request.forms.get('session_id')
	event_data = request.forms.get('event_data')
	data = service.event(session_id, event_data)
	response.content_type = 'application/json; charset=UTF8'
	return data


@app.route('/rsc', methods=['POST'])
def rsc():
	session_id = request.query.get('session_id')
	rsc_id = request.query.get('rsc_id')
	data_and_mime_type = service.resource(session_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		response.content_type = mime_type
		return data
	else:
		response.status=400
		return 'Unknown resource'

@app.route('/<filename:path>')
def serve_static(filename):
	return static_file(filename, root='static')


if __name__ == '__main__':
	run(app, host='localhost', port=5000)
