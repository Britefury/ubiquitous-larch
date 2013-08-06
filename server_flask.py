##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import webbrowser
import tempfile, os

from flask import Flask, request, Response, abort

from britefury.dynamicpage.service import UploadedFile
from britefury.projection.projection_service import CouldNotResolveLocationError

from larch import larch_app


service = larch_app.create_service()

app = Flask(__name__, static_url_path='/static', static_folder='static')


@app.route('/')
def index():
	try:
		return service.page()
	except CouldNotResolveLocationError:
		abort(404)


@app.route('/pages/<path:location>')
def page(location):
	get_params = {}
	get_params.update(request.args)
	try:
		return service.page(location, get_params)
	except CouldNotResolveLocationError:
		abort(404)


@app.route('/event/<session_id>', methods=['POST'])
def event(session_id):
	event_data = request.form['event_data']
	data = service.event(session_id, event_data)
	return Response(response=data, status=200, mimetype='application/json')


@app.route('/form/<session_id>', methods=['POST'])
def form(session_id):
	form_data = {}
	files = []

	for k in request.form.keys():
		form_data[k] = request.form[k]
	for k in request.files:
		upload = request.files[k]

		fd, temp_file_path = tempfile.mkstemp()
		os.close(fd)
		os.remove(temp_file_path)

		upload.save(temp_file_path)

		f = UploadedFile(upload.name, open(temp_file_path, 'rb'))

		form_data[k] = f
		files.append((f, temp_file_path))

	data = service.form(session_id, form_data)

	for f in files:
		f[0].file.close()
		os.remove(f[1])

	return Response(response=data, status=200, mimetype='application/json')


@app.route('/rsc/<session_id>/<rsc_id>', methods=['GET'])
def rsc(session_id, rsc_id):
	data_and_mime_type = service.resource(session_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		return Response(response=data, status=200, mimetype=mime_type)
	else:
		abort(404)




if __name__ == '__main__':
	print 'Point your browser at http://127.0.0.1:5000/ to try The Ubiquitous Larch'
	#webbrowser.get().open('http://127.0.0.1:5000/')
	app.run(debug=True)
	#app.run()
