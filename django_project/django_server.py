##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import webbrowser

from django.http import HttpResponse, Http404
from django.views.decorators.http import require_POST, require_GET

from britefury.projection.projection_service import CouldNotResolveLocationError

from larch import larch_app


service = larch_app.create_service()

def index(request):
	try:
		return HttpResponse(service.page())
	except CouldNotResolveLocationError:
		raise Http404



def page(request, location):
	try:
		get_params = {}
		get_params.update(request.GET)
		return HttpResponse(service.page(location, get_params))
	except CouldNotResolveLocationError:
		raise Http404


@require_POST
def event(request, session_id):
	event_data = request.POST['event_data']
	data = service.event(session_id, event_data)
	return HttpResponse(data, content_type='application/json')


@require_POST
def form(request, session_id):
	raise NotImplementedError, 'Form handling not implemented yet'
	# data = service.event(session_id, event_data)
	# return HttpResponse(data, content_type='application/json')


@require_GET
def rsc(request, session_id, rsc_id):
	data_and_mime_type = service.resource(session_id, rsc_id)
	if data_and_mime_type is not None:
		data, mime_type = data_and_mime_type
		return HttpResponse(data, content_type=mime_type)
	else:
		raise Http404



