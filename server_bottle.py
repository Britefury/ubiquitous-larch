##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import webbrowser

from bottle import Bottle, run, static_file, request, response

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
		return service.page(location)
	except CouldNotResolveLocationError:
		response.status = 404
		return 'Page at {0} not found'.format(location)


@app.route('/event', method='POST')
def event():
	session_id = request.forms.get('session_id')
	event_data = request.forms.get('event_data')
	data = service.event(session_id, event_data)
	response.content_type = 'application/json; charset=UTF8'
	return data


@app.route('/rsc', method='GET')
def rsc():
	session_id = request.query.get('session_id')
	rsc_id = request.query.get('rsc_id')
	data_and_mime_type = service.resource(session_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		response.content_type = mime_type
		return data
	else:
		response.status=404
		return 'Resource not found'

@app.route('/<filename:path>')
def serve_static(filename):
	return static_file(filename, root='static')


if __name__ == '__main__':
	print 'Point your browser at 127.0.0.1:5000 to try The Ubiquitous Larch'
	run(app, host='localhost', port=5000)
