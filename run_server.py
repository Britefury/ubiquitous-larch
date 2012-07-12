##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import datetime
import os
import sys
import cherrypy
import json
import random

from britefury.projection.subject import Subject
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.incremental_view.incremental_view import IncrementalView
from britefury.pres.presctx import PresentationContext
from britefury.pres.html import Html
from britefury.pres.pres import Pres, Key
from britefury.pres.controls.actionlink import action_link
from britefury.pres.controls.button import button
from britefury.default_perspective.default_perspective import DefaultPerspective
from britefury.message.event_message import EventMessage
from britefury.inspector.present_exception import present_exception



config = {'/':
			  {'tools.staticdir.on': True,
			   'tools.staticdir.dir': os.path.abspath('static'),
			   }
}


sample_code = """
from britefury.live.live_value import LiveValue
from britefury.live.live_function import LiveFunction
from britefury.pres.controls.button import button
from britefury.pres.html import Html


x=LiveValue(1)

y=LiveFunction(lambda: x.value*x.value)


def on_press():
    x.value = x.static_value + 1

b=button('Press me', on_press)

Html('<div>',x,'</div>', '<div>',b,'</div>', '<div>',y,'</div>')
"""

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
			return Html('<div>', self.__result[0], '</div>')


class CodeItem (object):
	def __init__(self, code):
		self.__code = code
		self.__result_container = CodeResult()

	def __present__(self, fragment, inherited_state):
		def on_change(event_name, ev_data):
			self.__code = ev_data

		def on_execute():
			lines = self.__code.split('\n')
			exec_code = self.__code
			eval_code = None
			for i in xrange(len(lines)-1, -1, -1):
				x = lines[i].strip()
				if x != ''  and  not x.startswith( '#' ):
					exec_code = '\n'.join(lines[:i])
					eval_code = lines[i]
					break
			env = {'CodeItem' : CodeItem}
			try:
				exec exec_code in env
				result = [eval(eval_code, env)]   if eval_code is not None   else None
			except Exception, e:
				self.__result_container.result = [present_exception(e, sys.exc_info()[2])]
			else:
				self.__result_container.result = result

		def on_execute_key(key):
			print 'Executing...'
			on_execute()


		code_area = Html('<textarea class="python_code">{code}</textarea>'.format(code=self.__code)).call_js('__pythonCodeArea.initPythonCodeArea').with_event_handler('changed', on_change)
		execute_button = button('Execute', on_execute)
		res = self.__result_container

		code_area_with_key_handler = code_area.with_key_handler([Key(Key.KEY_DOWN, 13, ctrl=True)], on_execute_key)

		return Html('<div>', code_area_with_key_handler, execute_button, res, '</div>')


class IndexPage (object):
	def __init__(self):
		self.__items = [CodeItem(sample_code)]
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
		#t1 = datetime.datetime.now()
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
		result = json.dumps([message.__to_json__()   for message in client_messages])
		#t2 = datetime.datetime.now()
		#delta_t = t2 - t1
		#print 'Event response time {0} for {1} messages, {2} chars'.format(delta_t, len(client_messages), len(str(result)))
		return result

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
