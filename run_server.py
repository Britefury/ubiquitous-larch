import os
import cherrypy

from britefury.projection.subject import Subject
from britefury.incremental_view.incremental_view import IncrementalView
from britefury.pres.presctx import PresentationContext
from britefury.pres.html import Html
from britefury.default_perspective.default_perspective import DefaultPerspective



config = {'/':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}


class IndexItem (object):
	def __init__(self, text):
		self.__text = text

	def __present__(self, fragment, inherited_state):
		return Html('<p>{0}</p>'.format(self.__text))


class IndexPage (object):
	def __init__(self):
		self.__items = [IndexItem('Paragraph 1'), IndexItem('Paragraph 2')]

	def __present__(self, fragment, inherited_state):
		return Html('<h1>Index page</h1>', *self.__items)


index_page = IndexPage()


index_subject = Subject(index_page)


index_view = IncrementalView(index_subject)


index_pres = index_view.view_pres

index_elem = index_pres.build(None)



class WebCombinatorServer (object):
	def index(self):
		return index_elem.__html__()
	index.exposed = True


root = WebCombinatorServer()
cherrypy.server.socket_port = 8000
cherrypy.quickstart(root, config=config)
