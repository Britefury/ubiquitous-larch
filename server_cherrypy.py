##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os
import webbrowser

import cherrypy

from britefury.projection.projection_service import CouldNotResolveLocationError

from larch import larch_app


config = {'/static/':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}



class WebCombinatorServer (object):
	def __init__(self):
		self.service = larch_app.create_service()


	def index(self):
		try:
			return self.service.page()
		except CouldNotResolveLocationError:
			cherrypy.response.status = 404
			return 'Document not found'

	index.exposed = True



	def pages(self, *location_components):
		try:
			return self.service.page('/'.join(location_components))
		except CouldNotResolveLocationError:
			cherrypy.response.status = 404
			return 'Document not found'

	pages.exposed = True



	def event(self, session_id, event_data):
		return self.service.event(session_id, event_data)

	event.exposed = True


	def rsc(self, session_id, rsc_id):
		data_and_mime_type = self.service.resource(session_id, rsc_id)
		if data_and_mime_type is not None:
			data, mime_type = data_and_mime_type
			cherrypy.response.headers['Content-Type'] = mime_type
			return data
		else:
			cherrypy.response.status = 404
			return 'Resource not found'

	rsc.exposed = True



if __name__ == '__main__':
	print 'Point your browser at http://127.0.0.1:5000/ to try The Ubiquitous Larch'
	root = WebCombinatorServer()
	cherrypy.server.socket_port = 5000
	cherrypy.quickstart(root, config=config)
