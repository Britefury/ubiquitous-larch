##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.message.message import Message


class EventMessage (Message):
	def __init__(self, segment_id, event_name, ev_data):
		self.__segment_id = segment_id
		self.__event_name = event_name
		self.__ev_data = ev_data


	@property
	def segment_id(self):
		return self.__segment_id

	@property
	def event_name(self):
		return self.__event_name

	@property
	def ev_data(self):
		return self.__ev_data


	def __to_json__(self):
		return {'msgtype' : 'event', 'segment_id' : self.__segment_id, 'event_name' : self.__event_name, 'ev_data' : self.__ev_data}


	@classmethod
	def __from_json__(cls, json):
		if json['msgtype'] == 'event':
			return EventMessage(json['segment_id'], json['event_name'], json['ev_data'])
		else:
			raise TypeError, 'msgtype is not event'
