##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import os, sys

import cherrypy
from cherrypy import _cpreqbody

from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError

from larch.apps import larch_app


config = {'/static':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}



class LarchService (object):
	def __init__(self):
		self.service = larch_app.create_service()


	def index(self):
		raise cherrypy.HTTPRedirect('/pages')

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
			view_id = location_components[0]
			return self.service.event(view_id, event_data)
		else:
			cherrypy.response.status = 404
			return 'Invalid event URL'

	event.exposed = True


	def form(self, *location_components, **post_data):
		if len(location_components) == 1:
			view_id = location_components[0]

			form_data = {}

			for k, v in post_data.items():
				if isinstance(v, _cpreqbody.Entity):
					form_data[k] = UploadedFile(v.filename, v.file, cherrypy_upload=v)
				else:
					form_data[k] = v

			return self.service.form(view_id, form_data)
		else:
			cherrypy.response.status = 404
			return 'Invalid form URL'

	form.exposed = True


	def rsc(self, *location_components, **kwargs):
		if len(location_components) == 2:
			view_id, rsc_id = location_components
			data_and_mime_type = self.service.resource(view_id, rsc_id)
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
	port = 5000
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	print 'Point your browser at http://127.0.0.1:{0}/ to try The Ubiquitous Larch'.format(port)
	larch = LarchService()
	cherrypy.server.socket_port = port
	cherrypy.quickstart(larch, config=config)
