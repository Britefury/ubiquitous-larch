##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json
import traceback
import sys

from larch.core.dynamicpage.page import DynamicPage, EventHandleError
from larch.core.dynamicpage import messages, user
from larch.inspector import present_exception


__author__ = 'Geoff'

import random



class UploadedFile (object):
	def __init__(self, upload_name, fp, **kwargs):
		self.upload_name = upload_name
		self.file = fp
		self.__dict__.update(kwargs)



class DynamicPageService (object):
	"""
	Abstract dynamic page web service API

	A subclass that overrides initialise_page should be instantiated.

	A web app must use the page, event and resource methods to provide the service.
	"""


	class View (object):
		"""
		Session information

		Attributes:
			:var dynamic_page: the page
			:var view_data: the view data, initialised by a service that overrides DynamicPageService
			:var location: the location
			:var get_params: the get parameters
		"""
		def __init__(self):
			self.dynamic_page = None
			self.view_data = None
			self.location = None
			self.get_params = None




	def __init__(self):
		"""
		Constructor

		:return: DynamicPageService instance
		"""
		self.__views = {}
		self.__view_counter = 1
		self.__users = {}

		self.__rng = random.Random()




	def page(self, doc_url, location='', get_params=None, user=None):
		"""
		The web service will invoke this method when the user opens a page. The HTML returned must be send to the client.

		:param doc_url: The location suffix for event, form and resource URLs
		:param location: The location being access by the browser, identifying the content that the user wishes to see. You should set up your app so that all paths under a specific URL prefix should take the suffix and pass it as the location.
		:param get_params: The GET parameters received as part of the location
		:param user: The user, if a user is logged in
		:return: The HTML content to be sent to the client browser
		"""
		raise NotImplementedError, 'abstract'




	def new_view(self, doc_url, location='', get_params=None, user=None):
		"""
		Creates a new view, with a newly allocated ID.
		The view contains a dynamic page, a location, and get parameters

		:param doc_url: The location suffix for event, form and resource URLs
		:param location: The location being access by the browser, identifying the content that the user wishes to see. You should set up your app so that all paths under a specific URL prefix should take the suffix and pass it as the location.
		:param get_params: The GET parameters received as part of the location
		:param user: The user, if a user is logged in
		:return: The HTML content to be sent to the client browser
		"""
		view_id = self.__new_view_id()
		view = self.View()
		self.__views[view_id] = view

		if get_params is None:
			get_params = {}

		our_user = self.__get_user(user)

		dynamic_page = DynamicPage(self, doc_url, view_id, location, get_params, our_user)
		view.dynamic_page = dynamic_page
		view.location = location
		view.get_params = get_params

		return view




	def event(self, view_id, event_data):
		"""
		Event response. Map the URL <root_url>/event/<view_id> to this. You will need to extract the view_id from the URL and the event_data field from the POST data and pass them through

		:param view_id: view_id field from URL
		:param event_data: event_data field from POST data
		:return: JSON string to send to the client browser
		"""

		# Get the page for the given view
		try:
			view = self.__views[view_id]
		except KeyError:
			msg = messages.invalid_page_message()
			client_messages = [msg]
			result = json.dumps(client_messages)
			return result


		dynamic_page = view.dynamic_page

		# Get the event messages
		block_json = json.loads(event_data)
		events_json = block_json['messages']

		return self.__handle_events(dynamic_page, events_json)



	def form(self, view_id, form_data):
		"""
		Form response. Map the URL <root_url>/form/<view_id> to this. You will need to extract the view_id from the URL and pass it as the first argument, along with the POST data as the second

		:param view_id: view_id field from URL
		:param form_data: the post data
		:return: JSON string to send to the client browser
		"""

		# Get the page for the given view
		try:
			view = self.__views[view_id]
		except KeyError:
			msg = messages.invalid_page_message()
			client_messages = [msg]
			result = json.dumps(client_messages)
			return result


		dynamic_page = view.dynamic_page

		# Build the form event
		ev_data = {}
		ev_data.update(form_data)
		segment_id = ev_data.pop('__larch_segment_id')
		events_json = [{'segment_id': segment_id, 'event_name': 'form_submit', 'ev_data': ev_data}]

		return self.__handle_events(dynamic_page, events_json)



	def __handle_events(self, dynamic_page, events_json):
		error_messages = []

		dynamic_page.lock()

		# Handle the events
		for ev_json in events_json:
			event_handle_result = dynamic_page.handle_event(ev_json['segment_id'], ev_json['event_name'], ev_json['ev_data'])
			if isinstance(event_handle_result, EventHandleError):
				msg = event_handle_result.to_message()
				error_messages.append(msg)


		# Synchronise the view
		try:
			client_messages = dynamic_page.synchronize()
		except Exception, e:
			# Catch internal server error
			err_html = present_exception.exception_to_html_src(e, sys.exc_info()[1], sys.exc_info()[2])
			msg = messages.error_during_update_message(err_html)
			error_messages.append(msg)
			client_messages = []

		# Send messages to the client
		result = json.dumps(client_messages + error_messages)

		#print 'EVENT {0}: in {1} events, out {2} messages'.format(block_json['id'], len(events_json), len(client_messages))

		dynamic_page.unlock()

		return result




	def resource(self, view_id, rsc_id):
		"""
		Resource acquisition. Map the URL <root_url>/rsc to this. You will need to extract the view_id and rsc_id fields from the GET parameters and pass them through

		:param view_id: view_id field from GET parameters
		:param rsc_id: rsc_id field from GET parameters
		:return: the data to send to the client and its MIME type in the form of a tuple: (data, mime_type)
		"""

		# Get the page for the given view
		try:
			view = self.__views[view_id]
		except KeyError:
			return None

		dynamic_page = view.dynamic_page

		dynamic_page.lock()

		# Get the resource
		try:
			result = dynamic_page.get_url_resource_data(rsc_id)
		except Exception:
			print 'Error while retrieving resource:'
			traceback.print_exc()
			return None
		finally:
			dynamic_page.unlock()

		return result



	def new_uploaded_file(self, upload_name):
		return UploadedFile(upload_name)



	def _close_page(self, page):
		view_id = page._view_id
		try:
			del self.__views[view_id]
		except KeyError:
			pass





	def __get_user(self, user):
		if user is None:
			return None

		try:
			return self.__users[user.user_id]
		except KeyError:
			self.__users[user.user_id] = user
			return user




	def __new_view_id(self):
		index = self.__view_counter
		self.__view_counter += 1
		salt = self.__rng.randint(0, 1<<31)
		view_id = 'v{0}{1}'.format(index, salt)
		return view_id

