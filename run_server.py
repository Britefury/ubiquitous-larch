import os
import cherrypy
import json
import random

from britefury.projection.subject import Subject
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.incremental_view.incremental_view import IncrementalView
from britefury.pres.presctx import PresentationContext
from britefury.pres.html import Html
from britefury.pres.pres import Pres
from britefury.default_perspective.default_perspective import DefaultPerspective
from britefury.message.event_message import EventMessage



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
		def handle_event(event_name, ev_data):
			index_page.add_item(IndexItem('New paragraph'))

		return Html('<p><a href="javascript:" onclick="javascript:__larch.postEvent($(this),\'clicked\', {});">Action</a></p>').with_event_handler('clicked', handle_event)



class CodeResult (object):
	def __init__(self):
		self.__result = None
		self.__incr = IncrementalValueMonitor()


	@property
	def result(self):
		return self.__result

	@result.setter
	def result(self, r):
		self.__result = r
		self.__incr.on_changed()


	def __present__(self, fragment, inherited_state):
		self.__incr.on_access()
		if self.__result is None:
			return Html('<div></div>')
		else:
			return Html('<div>', str(self.__result[0]), '</div>')


class CodeItem (object):
	def __init__(self, code):
		self.__code = code
		self.__result_container = CodeResult()

	def __present__(self, fragment, inherited_state):
		def on_change(event_name, ev_data):
			self.__code = ev_data

		def on_execute(event_name, ev_data):
			lines = self.__code.split('\n')
			exec_code = self.__code
			eval_code = None
			for i in xrange(len(lines)-1, -1, -1):
				x = lines[i].strip()
				if x != ''  and  not x.startswith( '#' ):
					exec_code = '\n'.join(lines[:i])
					eval_code = lines[i]
					break
			env = {}
			exec exec_code in env
			result = [eval(eval_code, env)]   if eval_code is not None   else None
			self.__result_container.result = result


		code_area = Html('<textarea class="python_code">{code}</textarea>'.format(code=self.__code)).with_event_handler('changed', on_change)
		execute_button = Html('<p><a href="javascript:" onclick="javascript:__larch.postEvent($(this),\'clicked\', {});">Execute</a></p>').with_event_handler('clicked', on_execute)
		res = self.__result_container

		return Html('<div>', code_area, execute_button, res, '</div>')


class IndexPage (object):
	def __init__(self):
		self.__items = [ActionItem(), IndexItem('Paragraph 1'), IndexItem('Paragraph 2'), CodeItem('print \'Hello world\'')]
		self.__incr = IncrementalValueMonitor()


	def add_item(self, item):
		self.__items.append(item)
		self.__incr.on_changed()

	def __present__(self, fragment, inherited_state):
		self.__incr.on_access()
		return Html('<h1>Index page</h1>', *self.__items)


index_page = IndexPage()


index_subject = Subject(index_page, stylesheet_names=['codemirror/lib/codemirror.css'], script_names=['codemirror/lib/codemirror.js', 'codemirror/mode/python/python.js', 'codemirror_post.js'])




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
		# Get the view for the given session
		try:
			view = self.__sessions[session_id]
		except KeyError:
			return '[]'

		# Get the event message
		event_json = json.loads(event_data)
		msg = EventMessage.__from_json__(event_json)

		# Handle the event
		view.handle_event(msg.element_id, msg.event_name, msg.ev_data)

		# Synchronise the view
		client_messages = view.synchronize()

		# Send messages to the client
		return json.dumps([message.__to_json__()   for message in client_messages])

	event.exposed = True



	def __new_session_id(self):
		index = self.__session_counter
		self.__session_counter += 1
		salt = self.__rng.randint(0, 1<<31)
		session_id = 'session_{0}{1}'.format(index, salt)
		return session_id


root = WebCombinatorServer()
cherrypy.server.socket_port = 8000
cherrypy.quickstart(root, config=config)
