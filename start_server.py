##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
#import webbrowser

from bottle import Bottle, run, static_file, request, response, redirect

from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError

from larch.apps import larch_app


service = larch_app.create_service()


app = Bottle()


@app.route('/')
def index():
	redirect('/pages')


@app.route('/pages')
@app.route('/pages/')
def root_page():
	try:
		get_params = {}
		get_params.update(request.params)
		return service.page('', get_params)
	except CouldNotResolveLocationError:
		response.status = 404
		return 'Page at {0} not found'.format('')


@app.route('/pages/<location:path>')
def page(location):
	try:
		get_params = {}
		get_params.update(request.params)
		return service.page(location, get_params)
	except CouldNotResolveLocationError:
		response.status = 404
		return 'Page at {0} not found'.format(location)


@app.route('/event/<view_id>', method='POST')
def event(view_id):
	event_data = request.forms.get('event_data')
	data = service.event(view_id, event_data)
	response.content_type = 'application/json; charset=UTF8'
	return data


@app.route('/form/<view_id>', method='POST')
def form(view_id):
	form_data = {}

	for k in request.forms.keys():
		form_data[k] = request.forms.get(k)
	for k in request.files.keys():
		upload = request.files.get(k)
		f = UploadedFile(upload.filename, upload.file)
		form_data[k] = f

	data = service.form(view_id, form_data)

	response.content_type = 'application/json; charset=UTF8'
	return data


@app.route('/rsc/<view_id>/<rsc_id>', method='GET')
def rsc(view_id, rsc_id):
	data_and_mime_type = service.resource(view_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		response.content_type = mime_type
		return data
	else:
		response.status=404
		return 'Resource not found'

@app.route('/static/<filename:path>')
def serve_static(filename):
	return static_file(filename, root='static')


if __name__ == '__main__':
	print 'Point your browser at http://127.0.0.1:5000/ to try The Ubiquitous Larch'
	run(app, host='localhost', port=5000)
