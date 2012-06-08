##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************


class Message (object):
	def __to_json__(self):
		raise NotImplementedError, 'abstract'


	@classmethod
	def __from_json__(cls, json):
		raise NotImplementedError, 'abstract'