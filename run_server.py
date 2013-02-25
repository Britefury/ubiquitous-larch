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

from britefury.projection.subject import Subject
from britefury.incremental.incremental_value_monitor import IncrementalValueMonitor
from britefury.incremental_view.incremental_view import IncrementalView
from britefury.pres.presctx import PresentationContext
from britefury.pres.html import Html
from britefury.pres.pres import Pres, Key
from britefury.pres.controls import action_link, button
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
from britefury.pres.controls import button
from britefury.pres.html import Html


x=LiveValue(1)

y=LiveFunction(lambda: x.value*x.value)


def on_press():
    x.value = x.static_value + 1

b=button.button('Press me', on_press)

Html(x,b,y)

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


class PythonCode (object):
	def __init__(self, code, editable=True):
		self.__code = code
		self.__editable = editable
		self.__incr = IncrementalValueMonitor()


	@property
	def editable(self):
		return self.__editable

	@editable.setter
	def editable(self, e):
		self.__editable = e
		self.__incr.on_changed()


	@property
	def code(self):
		return self.__code


	def __present__(self, fragment, inherited_state):
		self.__incr.on_access()

		def on_change(event_name, ev_data):
			self.__code = ev_data

		initialiser = '__pythonCodeArea.initPythonCodeArea'   if self.__editable   else '__pythonCodeArea.initPythonCodeAreaNonEditable'
		code_area = Html('<textarea class="python_code">{code}</textarea>'.format(code=self.__code)).call_js(initialiser)
		code_area = Html('<div>', code_area, '</div>').with_event_handler('changed', on_change)

		return Html('<div>', code_area, '</div>')



class ConsoleBlock (object):
	def __init__(self, code, result):
		assert isinstance(code, PythonCode)
		self.__code = code
		self.__result = result


	def __present__(self, fragment, inherited_state):
		res = ['<div>', self.__result[0], '</div>']   if self.__result is not None  else []
		return Html(*(['<div>', self.__code, '</div>'] + res))



class CurrentBlock (object):
	def __init__(self, code, console):
		self.__python_code = PythonCode(code)
		self.__console = console


	@property
	def python_code(self):
		return self.__python_code


	def __present__(self, fragment, inherited_state):
		def on_execute():
			self.__console._execute_current_block(self)

		def on_execute_key(key):
			on_execute()
			return True


		code_area = Html('<div>', self.__python_code, '</div>')
		execute_button = button.button('Execute', on_execute)

		code_area_with_key_handler = code_area.with_key_handler([Key(Key.KEY_DOWN, 13, ctrl=True)], on_execute_key)

		return Html('<div>', code_area_with_key_handler, execute_button, '</div>')





class Console (object):
	def __init__(self, code=''):
		self.__blocks = []
		self.__current_block = CurrentBlock(code, self)
		self.__incr = IncrementalValueMonitor()
		self._module = imp.new_module('<Console>')



	def _execute_current_block(self, block):
		lines = block.python_code.code.split('\n')
		exec_code = block.python_code.code
		eval_code = None
		for i in xrange(len(lines)-1, -1, -1):
			x = lines[i].strip()
			if x != ''  and  not x.startswith( '#' ):
				exec_code = '\n'.join(lines[:i])
				eval_code = lines[i]
				break
		env = self._module.__dict__
		try:
			exec exec_code in env
			result = [eval(eval_code, env)]   if eval_code is not None   else None
		except Exception, e:
			result = [present_exception(e, sys.exc_info()[2])]

		block.python_code.editable = False
		self.__blocks.append(ConsoleBlock(block.python_code, result))
		self.__current_block = CurrentBlock('', self)
		self.__incr.on_changed()


	def __present__(self, fragment, inherited_state):
		self.__incr.on_access()

		contents = []
		for block in self.__blocks + [self.__current_block]:
			contents.extend(['<div>', block, '</div>'])



		return Html(*contents)


class IndexPage (object):
	def __init__(self):
		self.__items = [Console(sample_code)]
		self.__incr = IncrementalValueMonitor()


	def add_item(self, item):
		self.__items.append(item)
		self.__incr.on_changed()

	def __present__(self, fragment, inherited_state):
		self.__incr.on_access()
		contents = ['<div><h1>Index page</h1>'] + self.__items + ['</div>']
		return Html(*contents)


index_page = IndexPage()


index_subject = Subject(None, index_page, stylesheet_names=['codemirror/lib/codemirror.css'], script_names=['codemirror/lib/codemirror.js', 'codemirror/mode/python/python.js', 'codemirror_post.js'])




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
