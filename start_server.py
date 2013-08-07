##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
#import webbrowser

from bottle import Bottle, run, static_file, request, response

from britefury.dynamicpage.service import UploadedFile
from britefury.projection.projection_service import CouldNotResolveLocationError

from larch import larch_app


service = larch_app.create_service()


app = Bottle()


@app.route('/')
def index():
	try:
		return service.page()
	except CouldNotResolveLocationError:
		response.status = 404
		return 'Document not found'


@app.route('/pages/<location:path>')
def page(location):
	try:
		get_params = {}
		get_params.update(request.params)
		return service.page(location, get_params)
	except CouldNotResolveLocationError:
		response.status = 404
		return 'Page at {0} not found'.format(location)


@app.route('/event/<session_id>', method='POST')
def event(session_id):
	event_data = request.forms.get('event_data')
	data = service.event(session_id, event_data)
	response.content_type = 'application/json; charset=UTF8'
	return data


@app.route('/form/<session_id>', method='POST')
def form(session_id):
	form_data = {}

	for k in request.forms.keys():
		form_data[k] = request.forms.get(k)
	for k in request.files.keys():
		upload = request.files.get(k)
		f = UploadedFile(upload.filename, upload.file)
		form_data[k] = f

	data = service.form(session_id, form_data)

	response.content_type = 'application/json; charset=UTF8'
	return data


@app.route('/rsc/<session_id>/<rsc_id>', method='GET')
def rsc(session_id, rsc_id):
	data_and_mime_type = service.resource(session_id, rsc_id)
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
