##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.message.message import Message


class EventMessage (Message):
	def __init__(self, element_id, event_name, ev_data):
		self.__element_id = element_id
		self.__event_name = event_name
		self.__ev_data = ev_data


	@property
	def element_id(self):
		return self.__element_id

	@property
	def event_name(self):
		return self.__event_name

	@property
	def ev_data(self):
		return self.__ev_data


	def __to_json__(self):
		return {'msgtype' : 'event', 'element_id' : self.__element_id, 'event_name' : self.__event_name, 'ev_data' : self.__ev_data}


	@classmethod
	def __from_json__(cls, json):
		if json['msgtype'] == 'event':
			return EventMessage(json['element_id'], json['event_name'], json['ev_data'])
		else:
			raise TypeError, 'msgtype is not event'
