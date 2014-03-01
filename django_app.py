##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************

import tempfile
import os

from django.http import HttpResponse, Http404
from django.middleware.csrf import get_token
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import requires_csrf_token, csrf_protect, csrf_exempt, ensure_csrf_cookie
from django.shortcuts import redirect, render_to_response, render
from django.template import Template, RequestContext
from larch.core.dynamicpage.service import UploadedFile
from larch.core.dynamicpage import user
from larch.core.projection_service import CouldNotResolveLocationError
from larch.apps import larch_app
from larch.hub import larch_hub

import django_settings
import ularch_auth


logout_url_path = None   if django_settings.ULARCH_RUNNING_LOCALLY   else '/accounts/logout'


hub = larch_hub.start_hub_and_client('main', 'larchapp', larch_app.create_service, '/main/larchapp', django_settings.ULARCH_DOCUMENTS_PATH, documentation_path=django_settings.ULARCH_DOCUMENTATION_PATH,
				     logout_url_path=logout_url_path)




if django_settings.ULARCH_RUNNING_LOCALLY:
	def login_required(f):
		return f
else:
	def login_required(fn):
		def check_logged_in(request, *args, **kwargs):
			if ularch_auth.is_authenticated(request.session):
				return fn(request, *args, **kwargs)
			else:
				path = request.path
				request.session['next_path'] = path
				return redirect('/accounts/login')
		check_logged_in.__name__ = fn.__name__
		return check_logged_in


@login_required
def index(request):
	return redirect('/pages/main/larchapp')



@login_required
def root_page(request):
	return redirect('/pages/main/larchapp')


@login_required
def front_page(request, category, name):
	try:
		get_params = {}
		get_params.update(request.GET)
		return HttpResponse(hub.page(category, name, '', get_params, user=ularch_auth.get_user(request.session)))
	except CouldNotResolveLocationError:
		raise Http404


@login_required
def page(request, category, name, location):
	try:
		get_params = {}
		get_params.update(request.GET)
		return HttpResponse(hub.page(category, name, location, get_params, user=ularch_auth.get_user(request.session)))
	except CouldNotResolveLocationError:
		raise Http404


@require_POST
@login_required
def event(request, category, name, view_id):
	event_data = request.POST['event_data']
	data = hub.event(category, name, view_id, event_data)
	return HttpResponse(data, content_type='application/json')


@require_POST
@login_required
def form(request, category, name, view_id):
	form_data = {}

	for k in request.POST.keys():
		form_data[k] = request.POST[k]

	files = []
	for k in request.FILES:
		upload = request.FILES[k]

		fd, temp_file_path = tempfile.mkstemp()
		os.close(fd)
		os.remove(temp_file_path)

		f = open(temp_file_path, 'wb')
		for chunk in upload.chunks():
			f.write(chunk)
		f.close()

		f = UploadedFile(upload.name, open(temp_file_path, 'rb'), flask_upload=upload)

		form_data[k] = f

		files.append((f, temp_file_path))

	data = hub.form(category, name, view_id, form_data)

	for f in files:
		f[0].file.close()
		os.remove(f[1])

	return HttpResponse(data, content_type='application/json')


@require_GET
@login_required
def rsc(request, category, name, view_id, rsc_id):
	data_and_mime_type = hub.resource(category, name, view_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		return HttpResponse(data, content_type=mime_type)
	else:
		raise Http404




def _csrf_hidden_input(request):
	return '<input type="hidden" name="csrfmiddlewaretoken" value="{0}"/>'.format(get_token(request))


@ensure_csrf_cookie
def login_form(request):
	if ularch_auth.is_authenticated(request.session):
		return redirect('/pages')
	else:
		csrf_token = _csrf_hidden_input(request)
		return HttpResponse(ularch_auth.login_form_page.format(status_msg='', csrf_token=csrf_token), RequestContext(request))


@ensure_csrf_cookie
def process_login(request):
	username = request.POST['username']
	password = request.POST['password']
	if ularch_auth.authenticate(request.session, username, password, django_settings.ULARCH_GLOBAL_PASSWORD):
		next_path = request.session.get('next_path')
		if next_path is None:
			next_path = '/pages'
		return redirect(next_path)
	else:
		csrf_token = _csrf_hidden_input(request)
		return HttpResponse(ularch_auth.login_form_page.format(status_msg='<p>Incorrect password; please try again.</p>', csrf_token=csrf_token), RequestContext(request))



def account_logout(request):
	ularch_auth.deauthenticate(request.session)
	return redirect('/')



def security_warning(request):
	return HttpResponse(ularch_auth.get_security_warning_page('django_settings.py'))