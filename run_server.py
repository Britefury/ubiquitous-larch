##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os

from flask import Flask, request, Response

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


app = Flask(__name__, static_url_path='', static_folder='static')


service = DynamicDocumentService(lambda dynamic_document: IncrementalView(index_subject, dynamic_document))

@app.route('/')
def index():
	return service.index()


@app.route('/event', methods=['POST'])
def event():
	if request.method == 'POST':
		session_id = request.form['session_id']
		event_data = request.form['event_data']
		data = service.event(session_id, event_data)
		return Response(response=data, status=200, mimetype='application/json')
	else:
		return


@app.route('/rsc', methods=['POST'])
def rsc():
	session_id = request.form['session_id']
	rsc_id = request.form['rsc_id']
	data, mime_type = service.resource(session_id, rsc_id)
	return Response(response=data, status=200, mimetype=mime_type)




if __name__ == '__main__':
	app.run(debug=True)
