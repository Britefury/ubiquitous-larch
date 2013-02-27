##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import datetime
import os
import sys
import cherrypy
import json
import random
import imp
import _ast
from britefury.dynamicsegments.service import DynamicDocumentService

from britefury.projection.subject import Subject
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.incremental_view.incremental_view import IncrementalView
from britefury.pres.presctx import PresentationContext
from britefury.pres.html import Html
from britefury.pres.pres import Pres, Key
from britefury.pres.controls import action_link, button, code_mirror
from britefury.default_perspective.default_perspective import DefaultPerspective
from britefury.message.event_message import EventMessage
from britefury.inspector.present_exception import present_exception
from larch.console.console import Console



config = {'/':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}


sample_code = """
from britefury.live.live_value import LiveValue
from britefury.live.live_function import LiveFunction
from britefury.pres.controls import button
from britefury.pres.html import Html


x=LiveValue(1)

y=LiveFunction(lambda: x.value*x.value)


def on_press():
    x.value = x.static_value + 1

b=button.button('Press me', on_press)

Html(x,b,y)

"""

sample_code = """
from britefury.live.live_value import LiveValue
from britefury.live.live_function import LiveFunction
from britefury.pres.controls import button, action_link
from britefury.pres.controls.expander import dropdown_expander
from britefury.pres.html import Html


aa = dropdown_expander( Html('Header'), Html('content') )


x=LiveValue(1)

y=LiveFunction(lambda: x.value*x.value)


def on_press():
    x.value = x.static_value + 1

b=button.button('Press me', on_press)

bb = Html(x,b,y)

aa
"""


console = Console()
index_subject = Subject(None, console, stylesheet_names=['codemirror/lib/codemirror.css'], script_names=['codemirror/lib/codemirror.js', 'codemirror/mode/python/python.js', 'codemirror_post.js'])




class WebCombinatorServer (object):
	def __init__(self):
		self.service = DynamicDocumentService(self.__init_document)


	def __init_document(self, dynamic_document):
		return IncrementalView(index_subject, dynamic_document)


	def index(self):
		return self.service.index()

	index.exposed = True



	def event(self, session_id, event_data):
		return self.service.event(session_id, event_data)

	event.exposed = True



root = WebCombinatorServer()
cherrypy.server.socket_port = 5000
cherrypy.quickstart(root, config=config)
