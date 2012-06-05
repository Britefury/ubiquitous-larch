import os
import cherrypy
import json

from britefury.projection.subject import Subject
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
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


class ActionItem (object):
	def __present__(self, fragment, inherited_state):
		return Html('<p><a href="javascript:postEvent(0)">Action</a></p>')


class IndexPage (object):
	def __init__(self):
		self.__items = [ActionItem(), IndexItem('Paragraph 1'), IndexItem('Paragraph 2')]
		self.__incr = IncrementalValueMonitor()


	def add_item(self, item):
		self.__items.append(item)
		self.__incr.on_changed()

	def __present__(self, fragment, inherited_state):
		self.__incr.on_access()
		return Html('<h1>Index page</h1>', *self.__items)


index_page = IndexPage()


index_subject = Subject(index_page)


index_view = IncrementalView(index_subject)


index_pres = index_view.view_pres

index_elem = index_pres.build(None)
index_elem.execute_queued_events()



class WebCombinatorServer (object):
	def index(self):
		return index_elem.__html__()
	index.exposed = True


	def event(self):
		index_page.add_item(IndexItem('Paragraph 3'))
		index_elem.execute_queued_events()
		cmds = index_elem.get_client_command_queue()
		index_elem.clear_client_command_queue()
		return json.dumps(cmds)

	event.exposed = True


root = WebCombinatorServer()
cherrypy.server.socket_port = 8000
cherrypy.quickstart(root, config=config)
