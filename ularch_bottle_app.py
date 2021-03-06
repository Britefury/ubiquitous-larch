##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
##-*************************
import os, datetime

from bottle import Bottle, static_file, request, response, redirect

from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError

from larch.apps import larch_app
from larch.hub import larch_hub

import ularch_auth


def make_ularch_bottle_app(docpath=None, documentation_path=None, running_locally=False, global_password='', session_time_hours=24):
	# Bottle app
	app = Bottle()


	#
	# VERY BASIC SESSION SYSTEM
	# (We build our own as Bottle does not provide one)
	#

	class Session (object):
		def __init__(self):
			self.expiry = datetime.datetime.now() + datetime.timedelta(hours=session_time_hours)

			self.attrs = {}


		def __getitem__(self, item):
			return self.attrs[item]

		def __setitem__(self, key, value):
			self.attrs[key] = value

		def __delitem__(self, key):
			del self.attrs[key]

		def get(self, key, default=None):
			return self.attrs.get(key, default)


	app_secret = os.urandom(32)

	sessions = {}

	def get_session():
		session_key = request.get_cookie('ularch_session_key', secret=app_secret)
		if session_key is not None:
			session = sessions.get(session_key)
			if session is not None:
				if datetime.datetime.now() < session.expiry:
					return session

		# New session
		session_key = os.urandom(16)
		session = Session()
		sessions[session_key] = session
		response.set_cookie('ularch_session_key', session_key, secret=app_secret, max_age=session_time_hours*3600, path='/')
		return session


	#
	# STATIC FILES
	#

	@app.route('/static/<filename:path>')
	def serve_static(filename):
		return static_file(filename, root='static')




	if not running_locally and (global_password is None  or  global_password == ''):
		#
		# We are NOT running locally and no password has been set
		# Display a security warning on all URLs
		#
		@app.route('/')
		def root():
			return ularch_auth.get_security_warning_page('wsgi_larch.py')

		@app.route('/<location:path>')
		def anything(location):
			return ularch_auth.get_security_warning_page('wsgi_larch.py')

	else:
		if not running_locally:
			#
			# We are not running locally
			# So this is accessible to a public server
			# We must provide authentication
			#


			#
			# Login URLs
			#

			@app.route('/accounts/login')
			def login_form():
				if ularch_auth.is_authenticated(get_session()):
					return redirect('/pages')
				else:
					return ularch_auth.login_form_page.format(status_msg='', csrf_token='')

			@app.route('/accounts/process_login', method='POST')
			def process_login():
				username = request.forms['username']
				pwd = request.forms['password']

				if ularch_auth.authenticate(get_session(), username, pwd, global_password):
					session = get_session()
					next_path = session.get('next_path')
					if next_path is None:
						next_path = '/pages'
					return redirect(next_path)
				else:
					return ularch_auth.login_form_page.format(status_msg='<p>Incorrect password; please try again.</p>', csrf_token='')

			@app.route('/accounts/logout')
			def logout():
				ularch_auth.deauthenticate(get_session())
				return redirect('/')



			def login_required(fn):
				def check_logged_in(*args, **kwargs):
					if ularch_auth.is_authenticated(get_session()):
						return fn(*args, **kwargs)
					else:
						path = request.path
						session = get_session()
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
			redirect('/pages/main/larchapp')


		@app.route('/pages')
		@app.route('/pages/')
		@app.route('/pages/<category>/<name>')
		@app.route('/pages/<category>/<name>/')
		@login_required
		def root_page(category, name):
			try:
				get_params = {}
				get_params.update(request.params)
				return hub.page(category, name, '', get_params, user=ularch_auth.get_user(get_session()))
			except CouldNotResolveLocationError:
				response.status = 404
				return 'Page at {0} not found'.format('')


		@app.route('/pages/<category>/<name>/<location:path>')
		@login_required
		def page(category, name, location):
			try:
				get_params = {}
				get_params.update(request.params)
				return hub.page(category, name, location, get_params, user=ularch_auth.get_user(get_session()))
			except CouldNotResolveLocationError:
				response.status = 404
				return 'Page at {0} not found'.format(location)


		@app.route('/event/<category>/<name>/<view_id>', method='POST')
		@login_required
		def event(category, name, view_id):
			event_data = request.forms.get('event_data')
			data = hub.event(category, name, view_id, event_data)
			response.content_type = 'application/json; charset=UTF8'
			return data


		@app.route('/form/<category>/<name>/<view_id>', method='POST')
		@login_required
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
		@login_required
		def rsc(category, name, view_id, rsc_id):
			data_and_mime_type = hub.resource(category, name, view_id, rsc_id)
			if data_and_mime_type is not None:
				data, mime_type = data_and_mime_type
				response.content_type = mime_type
				return data
			else:
				response.status=404
				return 'Resource not found'





	return app
