##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import os, sys

import cherrypy
from cherrypy import _cpreqbody

from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError
from larch.hub import larch_hub

from larch.apps import larch_app


config = {'/static':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}



class LarchWebApp (object):
	def __init__(self, hub):
		self.hub = hub


	def index(self):
		raise cherrypy.HTTPRedirect('/pages/main/larchapp')

	index.exposed = True



	def pages(self, *location_components, **get_params):
		try:
			if len(location_components) >= 2:
				category = location_components[0]
				name = location_components[1]
				loc = '/'.join(location_components[2:])
				return self.hub.page(category, name, loc, get_params)
			else:
				raise cherrypy.HTTPRedirect('/pages/main/larchapp')
		except CouldNotResolveLocationError:
			cherrypy.response.status = 404
			return 'Document not found'

	pages.exposed = True



	def event(self, *location_components, **post_data):
		if len(location_components) == 3:
			category, name, view_id = location_components
			event_data = post_data.get('event_data')
			if event_data is None:
				cherrypy.response.status = 400
				return 'No event data'
			return self.hub.event(category, name, view_id, event_data)
		else:
			cherrypy.response.status = 404
			return 'Invalid event URL'

	event.exposed = True


	def form(self, *location_components, **post_data):
		if len(location_components) == 3:
			category, name, view_id = location_components

			form_data = {}

			for k, v in post_data.items():
				if isinstance(v, _cpreqbody.Entity):
					form_data[k] = UploadedFile(v.filename, v.file, cherrypy_upload=v)
				else:
					form_data[k] = v

			return self.hub.form(category, name, view_id, form_data)
		else:
			cherrypy.response.status = 404
			return 'Invalid form URL'

	form.exposed = True


	def rsc(self, *location_components, **kwargs):
		if len(location_components) == 4:
			category, name, view_id, rsc_id = location_components
			data_and_mime_type = self.hub.resource(category, name, view_id, rsc_id)
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
	options, args = larch_app.parse_cmd_line()
	hub = larch_hub.start_hub_and_client('main', 'larchapp', larch_app.create_service, '/main/larchapp', options, args)
	print 'Point your browser at http://127.0.0.1:{0}/ to try The Ubiquitous Larch'.format(options.port)
	larch = LarchWebApp(hub)
	cherrypy.server.socket_port = options.port
	cherrypy.quickstart(larch, config=config)
