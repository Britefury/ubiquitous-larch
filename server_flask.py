##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os

from flask import Flask, request, Response, abort

from larch import larch_app


service = larch_app.create_service()

app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/')
def index():
	data = service.index()
	if data is not None:
		return data
	else:
		abort(404)


@app.route('/pages/<path:location>')
def page(location):
	data = service.index(location)
	if data is not None:
		return data
	else:
		abort(404)


@app.route('/event', methods=['POST'])
def event():
	session_id = request.form['session_id']
	event_data = request.form['event_data']
	data = service.event(session_id, event_data)
	return Response(response=data, status=200, mimetype='application/json')


@app.route('/rsc', methods=['GET'])
def rsc():
	session_id = request.args['session_id']
	rsc_id = request.args['rsc_id']
	data_and_mime_type = service.resource(session_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		return Response(response=data, status=200, mimetype=mime_type)
	else:
		abort(404)




if __name__ == '__main__':
	app.run(debug=True)
