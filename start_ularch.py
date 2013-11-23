##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import webbrowser

import sys

from bottle import Bottle, run, static_file, request, response, redirect

from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError

from larch.apps import larch_app
from larch.hub import larch_hub


hub = None


app = Bottle()



@app.route('/static/<filename:path>')
def serve_static(filename):
	return static_file(filename, root='static')


@app.route('/')
def index():
	redirect('/pages/main/larchapp')


@app.route('/pages')
@app.route('/pages/')
@app.route('/pages/<category>/<name>')
@app.route('/pages/<category>/<name>/')
def root_page(category, name):
	try:
		get_params = {}
		get_params.update(request.params)
		return hub.page(category, name, '', get_params)
	except CouldNotResolveLocationError:
		response.status = 404
		return 'Page at {0} not found'.format('')


@app.route('/pages/<category>/<name>/<location:path>')
def page(category, name, location):
	try:
		get_params = {}
		get_params.update(request.params)
		return hub.page(category, name, location, get_params)
	except CouldNotResolveLocationError:
		response.status = 404
		return 'Page at {0} not found'.format(location)


@app.route('/event/<category>/<name>/<view_id>', method='POST')
def event(category, name, view_id):
	event_data = request.forms.get('event_data')
	data = hub.event(category, name, view_id, event_data)
	response.content_type = 'application/json; charset=UTF8'
	return data


@app.route('/form/<category>/<name>/<view_id>', method='POST')
def form(category, name, view_id):
	form_data = {}

	for k in request.forms.keys():
		form_data[k] = request.forms.get(k)
	for k in request.files.keys():
		upload = request.files.get(k)
		f = UploadedFile(upload.filename, upload.file)
		form_data[k] = f

	data = hub.form(category, name, view_id, form_data)

	response.content_type = 'application/json; charset=UTF8'
	return data


@app.route('/rsc/<category>/<name>/<view_id>/<rsc_id>', method='GET')
def rsc(category, name, view_id, rsc_id):
	data_and_mime_type = hub.resource(category, name, view_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		response.content_type = mime_type
		return data
	else:
		response.status=404
		return 'Resource not found'


if __name__ == '__main__':
	options = larch_app.parse_cmd_line()
	hub = larch_hub.start_hub_and_client('main', 'larchapp', larch_app.create_service, '/main/larchapp', options)
	print 'Point your browser at http://127.0.0.1:{0}/ to try The Ubiquitous Larch'.format(options.port)
	webbrowser.get().open('http://127.0.0.1:{0}/'.format(options.port))
	run(app, host='localhost', port=options.port)
else:
	hub = larch_hub.start_hub_and_client('main', 'larchapp', larch_app.create_service, '/main/larchapp')
