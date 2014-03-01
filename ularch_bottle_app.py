##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import webbrowser

import sys, os, datetime

from bottle import Bottle, static_file, request, response, redirect

from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError

from larch.apps import larch_app
from larch.hub import larch_hub

import ularch_pages


def make_ularch_bottle_app(docpath=None, documentation_path=None, running_locally=False, password='', session_time_hours=24):
	# Bottle app
	app = Bottle()


	#
	# STATIC FILES
	#

	@app.route('/static/<filename:path>')
	def serve_static(filename):
		return static_file(filename, root='static')




	if not running_locally and (password is None  or  password == ''):
		#
		# We are NOT running locally and no password has been set
		# Display a security warning on all URLs
		#
		@app.route('/')
		def root():
			return ularch_pages.security_warning_page

		@app.route('/<location:path>')
		def anything(location):
			return ularch_pages.security_warning_page

	else:
		if not running_locally:
			#
			# We are not running locally
			# So this is accessible to a public server
			# We must provide authentication
			#

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
			# Authentication functions
			#

			def is_authenticated():
				session = get_session()
				return session.get('authenticated', False)

			def authenticate(pwd_from_user):
				session = get_session()
				if pwd_from_user == password:
					session['authenticated'] = True
					return True
				else:
					return False

			def deauthenticate():
				session = get_session()
				if session.get('authenticated') is not None:
					del session['authenticated']


			#
			# Login URLs
			#

			@app.route('/accounts/login')
			def login_form():
				if is_authenticated():
					return redirect('/pages')
				else:
					return ularch_pages.login_form_page.format('')

			@app.route('/accounts/process_login', method='POST')
			def process_login():
				pwd = request.forms['password']

				if authenticate(pwd):
					session = get_session()
					next_path = session.get('next_path')
					if next_path is None:
						next_path = '/pages'
					return redirect(next_path)
				else:
					return ularch_pages.login_form_page.format('<p>Incorrect password; please try again.</p>')

			@app.route('/accounts/logout')
			def logout():
				deauthenticate()
				return redirect('/')



			def login_required(fn):
				def chech_logged_in(*args, **kwargs):
					if is_authenticated():
						return fn(*args, **kwargs)
					else:
						path = request.path
						session = get_session()
						session['next_path'] = path
						return redirect('/accounts/login')
				chech_logged_in.__name__ = fn.__name__
				return chech_logged_in

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
				return hub.page(category, name, '', get_params)
			except CouldNotResolveLocationError:
				response.status = 404
				return 'Page at {0} not found'.format('')


		@app.route('/pages/<category>/<name>/<location:path>')
		@login_required
		def page(category, name, location):
			try:
				get_params = {}
				get_params.update(request.params)
				return hub.page(category, name, location, get_params)
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
