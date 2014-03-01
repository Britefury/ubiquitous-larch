##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import os, tempfile

from flask import Flask, request, Response, abort, redirect, session

from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError

from larch.apps import larch_app
from larch.hub import larch_hub

import ularch_auth


def make_ularch_flask_app(docpath=None, documentation_path=None, running_locally=False, global_password='', session_time_hours=24):
	app = Flask(__name__, static_url_path='/static', static_folder='static')
	app.secret_key = os.urandom(32)



	if not running_locally and (global_password is None  or  global_password == ''):
		#
		# We are NOT running locally and no password has been set
		# Display a security warning on all URLs
		#
		@app.route('/')
		def root():
			return ularch_auth.get_security_warning_page('wsgi_larch_flask.py')

		@app.route('/<path:location>')
		def anything(location):
			return ularch_auth.get_security_warning_page('wsgi_larch_flask.py')

	else:
		if not running_locally:
			#
			# We are not running locally
			# So this is accessible to a public server
			# We must provide authentication
			#
			#
			# Authentication functions
			#


			#
			# Login URLs
			#

			@app.route('/accounts/login')
			def login_form():
				if ularch_auth.is_authenticated(session):
					return redirect('/pages')
				else:
					return ularch_auth.login_form_page.format(status_msg='', csrf_token='')

			@app.route('/accounts/process_login', methods=['POST'])
			def process_login():
				username = request.form['username']
				pwd = request.form['password']

				if ularch_auth.authenticate(session, username, pwd, global_password):
					next_path = session.get('next_path')
					if next_path is None:
						next_path = '/pages'
					return redirect(next_path)
				else:
					return ularch_auth.login_form_page.format(status_msg='<p>Incorrect password; please try again.</p>', csrf_token='')

			@app.route('/accounts/logout')
			def logout():
				ularch_auth.deauthenticate(session)
				return redirect('/')



			def login_required(fn):
				def check_logged_in(*args, **kwargs):
					if ularch_auth.is_authenticated(session):
						return fn(*args, **kwargs)
					else:
						path = request.path
						session['next_path'] = path
						return redirect('/accounts/login')
				check_logged_in.__name__ = fn.__name__
				return check_logged_in

			logout_url_path = '/accounts/logout'
		else:
			#
			# We are running locally:
			# no authentication
			#
			def login_required(f):
				return f

			logout_url_path = None


		#
		# Ubiquitous Larch URLs
		#


		hub = larch_hub.start_hub_and_client('main', 'larchapp', larch_app.create_service, '/main/larchapp', docpath, documentation_path=documentation_path, logout_url_path=logout_url_path)



		@app.route('/')
		@login_required
		def index():
			return redirect('/pages/main/larchapp')


		@app.route('/pages')
		@app.route('/pages/')
		@app.route('/pages/<category>/<name>')
		@app.route('/pages/<category>/<name>/')
		@login_required
		def root_page(category=None, name=None):
			get_params = {}
			get_params.update(request.args)
			if category is None  or  name is None:
				return redirect('/pages/main/larchapp')
			try:
				return hub.page(category, name, '', get_params, user=ularch_auth.get_user(session))
			except CouldNotResolveLocationError:
				abort(404)


		@app.route('/pages/<category>/<name>/<path:location>')
		@login_required
		def page(category, name, location):
			get_params = {}
			get_params.update(request.args)
			try:
				return hub.page(category, name, location, get_params, user=ularch_auth.get_user(session))
			except CouldNotResolveLocationError:
				abort(404)


		@app.route('/event/<category>/<name>/<view_id>', methods=['POST'])
		@login_required
		def event(category, name, view_id):
			event_data = request.form['event_data']
			data = hub.event(category, name, view_id, event_data)
			return Response(response=data, status=200, mimetype='application/json')


		@app.route('/form/<category>/<name>/<view_id>', methods=['POST'])
		@login_required
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


		@app.route('/rsc/<category>/<name>/<view_id>/<rsc_id>', methods=['GET'])
		@login_required
		def rsc(category, name, view_id, rsc_id):
			data_and_mime_type = hub.resource(category, name, view_id, rsc_id)
			if data_and_mime_type is not None:
				data, mime_type = data_and_mime_type
				return Response(response=data, status=200, mimetype=mime_type)
			else:
				abort(404)



	return app