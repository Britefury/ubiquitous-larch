##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import webbrowser

from django.http import HttpResponse, Http404

from britefury.projection.projection_service import CouldNotResolveLocationError

from larch import larch_app


service = larch_app.create_service()

def index(request):
	try:
		return HttpResponse(service.page())
	except CouldNotResolveLocationError:
		raise Http404

#
# @app.route('/pages/<path:location>')
# def page(location):
# 	try:
# 		return service.page(location)
# 	except CouldNotResolveLocationError:
# 		abort(404)
#
#
# @app.route('/event', methods=['POST'])
# def event():
# 	session_id = request.form['session_id']
# 	event_data = request.form['event_data']
# 	data = service.event(session_id, event_data)
# 	return Response(response=data, status=200, mimetype='application/json')
#
#
# @app.route('/rsc', methods=['GET'])
# def rsc():
# 	session_id = request.args['session_id']
# 	rsc_id = request.args['rsc_id']
# 	data_and_mime_type = service.resource(session_id, rsc_id)
# 	if data_and_mime_type is not None:
# 		data, mime_type = data_and_mime_type
# 		return Response(response=data, status=200, mimetype=mime_type)
# 	else:
# 		abort(404)
#
#
#
