##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json
from britefury.dynamicsegments.document import DynamicDocument
from britefury.message.event_message import EventMessage

__author__ = 'Geoff'

import random


class _Session (object):
	def __init__(self):
		self.dynamic_document = None
		self.session_data = None


class DynamicDocumentService (object):
	def __init__(self, document_initialiser_fn):
		self.__sessions = {}
		self.__session_counter = 1

		self.__rng = random.Random()

		self.__document_initialiser_fn = document_initialiser_fn


	def index(self):
		session_id = self.__new_session_id()
		session = _Session()
		self.__sessions[session_id] = session

		dynamic_document = DynamicDocument(session_id)
		session.dynamic_document = dynamic_document

		session_data = self.__document_initialiser_fn(dynamic_document)
		session.session_data = session_data

		return dynamic_document.page_html()



	def event(self, session_id, event_data):
		#t1 = datetime.datetime.now()
		# Get the view for the given session
		try:
			session = self.__sessions[session_id]
		except KeyError:
			return '[]'

		dynamic_document = session.dynamic_document

		dynamic_document.lock()

		# Get the event message
		event_json = json.loads(event_data)
		msg = EventMessage.__from_json__(event_json)

		# Handle the event
		dynamic_document.handle_event(msg.segment_id, msg.event_name, msg.ev_data)

		# Synchronise the view
		client_messages = dynamic_document.synchronize()

		# Send messages to the client
		result = json.dumps([message.__to_json__()   for message in client_messages])
		#t2 = datetime.datetime.now()
		#delta_t = t2 - t1
		#print 'Event response time {0} for {1} messages, {2} chars'.format(delta_t, len(client_messages), len(str(result)))

		dynamic_document.unlock()

		return result



	def __new_session_id(self):
		index = self.__session_counter
		self.__session_counter += 1
		salt = self.__rng.randint(0, 1<<31)
		session_id = 'session_{0}{1}'.format(index, salt)
		return session_id

