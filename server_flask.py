##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import tempfile
import os
import sys

from flask import Flask, request, Response, abort, redirect
from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError
from larch.apps import larch_app
from larch.hub import larch_hub


hub = None

app = Flask(__name__, static_url_path='/static', static_folder='static')


@app.route('/')
def index():
	return redirect('/main/larchapp/pages')


@app.route('/<category>/<name>')
@app.route('/<category>/<name>/')
@app.route('/<category>/<name>/pages')
@app.route('/<category>/<name>/pages/')
def root_page(category, name):
	get_params = {}
	get_params.update(request.args)
	try:
		return hub.page(category, name, '', get_params)
	except CouldNotResolveLocationError:
		abort(404)


@app.route('/<category>/<name>/pages/<path:location>')
def page(category, name, location):
	get_params = {}
	get_params.update(request.args)
	try:
		return hub.page(category, name, location, get_params)
	except CouldNotResolveLocationError:
		abort(404)


@app.route('/<category>/<name>/event/<view_id>', methods=['POST'])
def event(category, name, view_id):
	event_data = request.form['event_data']
	data = hub.event(category, name, view_id, event_data)
	return Response(response=data, status=200, mimetype='application/json')


@app.route('/<category>/<name>/form/<view_id>', methods=['POST'])
def form(category, name, view_id):
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

		f = UploadedFile(upload.filename, open(temp_file_path, 'rb'))

		form_data[k] = f
		files.append((f, temp_file_path))

	data = hub.form(category, name, view_id, form_data)

	for f in files:
		f[0].file.close()
		os.remove(f[1])

	return Response(response=data, status=200, mimetype='application/json')


@app.route('/<category>/<name>/rsc/<view_id>/<rsc_id>', methods=['GET'])
def rsc(category, name, view_id, rsc_id):
	data_and_mime_type = hub.resource(category, name, view_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		return Response(response=data, status=200, mimetype=mime_type)
	else:
		abort(404)




if __name__ == '__main__':
	options = larch_app.parse_cmd_line()
	hub = larch_hub.LarchDefaultHub()
	hub.new_kernel('main', 'larchapp', larch_app.create_service, '/main/larchapp', options)
	print 'Point your browser at http://127.0.0.1:{0}/ to try The Ubiquitous Larch'.format(options.port)
	#webbrowser.get().open('http://127.0.0.1:{0}/'.format(options.port))
	app.run(debug=True, port=options.port)
	#app.run()
else:
	hub = larch_hub.LarchDefaultHub()
	hub.new_kernel('main', 'larchapp', larch_app.create_service, '/main/larchapp')
