##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************

import tempfile
import os

from django.http import HttpResponse, Http404
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response, render
from django.template import Template, RequestContext
from larch.core.dynamicpage.service import UploadedFile
from larch.core.dynamicpage import user
from larch.core.projection_service import CouldNotResolveLocationError
from larch.apps import larch_app


service = larch_app.create_service(logout_url_path='/accounts/logout')


def _user_for_request(request):
	django_user = request.user
	if django_user.is_authenticated():
		return user.User(django_user.id, django_user.username)
	else:
		return None


@login_required
def index(request):
	try:
		return HttpResponse(service.page(user=_user_for_request(request)))
	except CouldNotResolveLocationError:
		raise Http404



@login_required
def root_page(request):
	try:
		get_params = {}
		get_params.update(request.GET)
		return HttpResponse(service.page('', get_params, user=_user_for_request(request)))
	except CouldNotResolveLocationError:
		raise Http404


@login_required
def page(request, location):
	try:
		get_params = {}
		get_params.update(request.GET)
		return HttpResponse(service.page(location, get_params, user=_user_for_request(request)))
	except CouldNotResolveLocationError:
		raise Http404


@require_POST
@login_required
def event(request, view_id):
	event_data = request.POST['event_data']
	data = service.event(view_id, event_data)
	return HttpResponse(data, content_type='application/json')


@require_POST
@login_required
def form(request, view_id):
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

	data = service.form(view_id, form_data)

	for f in files:
		f[0].file.close()
		os.remove(f[1])

	return HttpResponse(data, content_type='application/json')


@require_GET
@login_required
def rsc(request, view_id, rsc_id):
	data_and_mime_type = service.resource(view_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		return HttpResponse(data, content_type=mime_type)
	else:
		raise Http404







__login_template = Template("""
<html>
<head>
<title>Login</title>
<link rel="stylesheet" type="text/css" href="/static/jquery/css/ui-lightness/jquery-ui-1.10.2.custom.min.css"/>
<link rel="stylesheet" type="text/css" href="/static/larch.css"/>
<link rel="stylesheet" type="text/css" href="/static/larch_login.css"/>
<script type="text/javascript" src="/static/jquery/js/jquery-1.9.1.js"></script>
<script type="text/javascript" src="/static/jquery/js/jquery-ui-1.10.2.custom.min.js"></script>
</head>


<body>
<div class="title_bar">The Ubiquitous Larch</div>

<div class="login_form">
<p>Please login:</p>

<form action="/accounts/process_login" method="POST">{% csrf_token %}
<table>
	<tr><td>Username</td><td><input type="text" name="username" class="login_form_text_field"/></td></tr>
	<tr><td>Password</td><td><input type="password" name="password" class="login_form_text_field"/></td></tr>
	<tr><td></td><td><input id="submit_button" type="submit" value="Login"/></td></tr>
</table>
</form>
</div>

<script type="text/javascript">
	$("#submit_button").button();
</script>
</body>
</html>
""")


def login_form(request):
	ctx = RequestContext(request)
	return HttpResponse(__login_template.render(ctx), content_type='text/html')


def process_login(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None  and  user.is_active:
		login(request, user)
		return redirect('/pages')
	else:
		ctx = RequestContext(request, prompt='Bad login')
		return HttpResponse(__login_template.render(ctx), content_type='text/html')



def account_logout(request):
	logout(request)
	return redirect('/')