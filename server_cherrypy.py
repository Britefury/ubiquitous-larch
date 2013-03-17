##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import os
import cherrypy

import larch_app


config = {'/':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}



class WebCombinatorServer (object):
	def __init__(self):
		self.service = larch_app.create_service()


	def index(self):
		return self.service.index()

	index.exposed = True



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



root = WebCombinatorServer()
cherrypy.server.socket_port = 5000
cherrypy.quickstart(root, config=config)
