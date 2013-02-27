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
		self.__sessions = {}
		self.__session_counter = 1

		self.__rng = random.Random()


	def index(self):
		session_id = self.__new_session_id()
		view = IncrementalView(index_subject, session_id)
		self.__sessions[session_id] = view
		return view.root_html

	index.exposed = True



	def event(self, session_id, event_data):
		#t1 = datetime.datetime.now()
		# Get the view for the given session
		try:
			view = self.__sessions[session_id]
		except KeyError:
			return '[]'

		view.lock()

		# Get the event message
		event_json = json.loads(event_data)
		msg = EventMessage.__from_json__(event_json)

		# Handle the event
		view.handle_event(msg.segment_id, msg.event_name, msg.ev_data)

		# Synchronise the view
		client_messages = view.synchronize()

		# Send messages to the client
		result = json.dumps([message.__to_json__()   for message in client_messages])
		#t2 = datetime.datetime.now()
		#delta_t = t2 - t1
		#print 'Event response time {0} for {1} messages, {2} chars'.format(delta_t, len(client_messages), len(str(result)))

		view.unlock()

		return result

	event.exposed = True



	def __new_session_id(self):
		index = self.__session_counter
		self.__session_counter += 1
		salt = self.__rng.randint(0, 1<<31)
		session_id = 'session_{0}{1}'.format(index, salt)
		return session_id


root = WebCombinatorServer()
cherrypy.server.socket_port = 5000
cherrypy.quickstart(root, config=config)
