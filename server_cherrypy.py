##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import os
import webbrowser

import cherrypy

from britefury.projection.projection_service import CouldNotResolveLocationError

from larch import larch_app


config = {'/static':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}



class LarchService (object):
	def __init__(self):
		self.service = larch_app.create_service()


	def index(self):
		try:
			return self.service.page()
		except CouldNotResolveLocationError:
			cherrypy.response.status = 404
			return 'Document not found'

	index.exposed = True



	def pages(self, *location_components, **get_params):
		try:
			return self.service.page('/'.join(location_components), get_params)
		except CouldNotResolveLocationError:
			cherrypy.response.status = 404
			return 'Document not found'

	pages.exposed = True



	def event(self, *location_components, **post_data):
		if len(location_components) == 1:
			event_data = post_data.get('event_data')
			if event_data is None:
				cherrypy.response.status = 400
				return 'No event data'
			session_id = location_components[0]
			return self.service.event(session_id, event_data)
		else:
			cherrypy.response.status = 404
			return 'Invalid event URL'

	event.exposed = True


	def form(self, *location_components, **post_data):
		if len(location_components) == 1:
			session_id = location_components[0]

			raise NotImplementedError, 'CherryPy form handling not implemented; don\'t know how to differentiate file uploads yet'

			# event_data = post_data.get('event_data')
			# if event_data is None:
			# 	cherrypy.response.status = 400
			# 	return 'No event data'
			#
			# return self.service.event(session_id, event_data)
		else:
			cherrypy.response.status = 404
			return 'Invalid form URL'

	form.exposed = True


	def rsc(self, *location_components, **kwargs):
		if len(location_components) == 2:
			session_id, rsc_id = location_components
			data_and_mime_type = self.service.resource(session_id, rsc_id)
			if data_and_mime_type is not None:
				data, mime_type = data_and_mime_type
				cherrypy.response.headers['Content-Type'] = mime_type
				return data
			else:
				cherrypy.response.status = 404
				return 'Resource not found'
		else:
			cherrypy.response.status = 404
			return 'Invalid resource URL'
	rsc.exposed = True



if __name__ == '__main__':
	print 'Point your browser at http://127.0.0.1:5000/ to try The Ubiquitous Larch'
	larch = LarchService()
	cherrypy.server.socket_port = 5000
	cherrypy.quickstart(larch, config=config)
