##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json
import traceback
import sys
from britefury.dynamicsegments.document import DynamicDocument, EventHandleError
from britefury.dynamicsegments import messages
from britefury.inspector import present_exception

__author__ = 'Geoff'

import random


class _Session (object):
	def __init__(self):
		self.dynamic_document = None
		self.session_data = None


class DynamicDocumentService (object):
	def __init__(self):
		self.__sessions = {}
		self.__session_counter = 1

		self.__rng = random.Random()


	def initialise_session(self, dynamic_document, location):
		raise NotImplementedError, 'abstract'


	def page(self, location=None):
		session_id = self.__new_session_id()
		session = _Session()
		self.__sessions[session_id] = session

		dynamic_document = DynamicDocument(self, session_id)
		session.dynamic_document = dynamic_document

		try:
			session_data = self.initialise_session(dynamic_document, location)
		except:
			# Problem initialising the session; remove it and re-raise
			del self.__sessions[session_id]
			raise
		else:
			# Session okay, return HTML content
			session.session_data = session_data
			return dynamic_document.page_html()




	def event(self, session_id, event_data):
		# Get the document for the given session
		try:
			session = self.__sessions[session_id]
		except KeyError:
			msg = messages.invalid_page_message()
			client_messages = [msg]
			result = json.dumps(client_messages)
			return result


		dynamic_document = session.dynamic_document

		dynamic_document.lock()

		# Get the event messages
		events_json = json.loads(event_data)

		error_messages = []

		# Handle the events
		for ev_json in events_json:
			event_handle_result = dynamic_document.handle_event(ev_json['segment_id'], ev_json['event_name'], ev_json['ev_data'])
			if isinstance(event_handle_result, EventHandleError):
				# Catch internal server error
				err_html = present_exception.exception_to_html_src(event_handle_result.exception, event_handle_result.traceback)
				msg = messages.error_during_update_message(err_html)
				error_messages.append(msg)


		# Synchronise the view
		try:
			client_messages = dynamic_document.synchronize()
		except Exception, e:
			# Catch internal server error
			err_html = present_exception.exception_to_html_src(e, sys.exc_info()[2])
			msg = messages.error_during_update_message(err_html)
			error_messages.append(msg)
			client_messages = []

		# Send messages to the client
		result = json.dumps(client_messages + error_messages)

		dynamic_document.unlock()

		return result


	def resource(self, session_id, rsc_id):
		# Get the document for the given session
		try:
			session = self.__sessions[session_id]
		except KeyError:
			return None

		dynamic_document = session.dynamic_document

		dynamic_document.lock()

		# Get the resource
		try:
			result = dynamic_document.get_resource_data(rsc_id)
		except Exception:
			print 'Error while retrieving resource:'
			traceback.print_exc()
			return None
		finally:
			dynamic_document.unlock()

		return result




	def __new_session_id(self):
		index = self.__session_counter
		self.__session_counter += 1
		salt = self.__rng.randint(0, 1<<31)
		session_id = 'session_{0}{1}'.format(index, salt)
		return session_id

