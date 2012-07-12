##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.message.message import Message


class ExecuteJSMessage (Message):
	def __init__(self, js_code):
		self.__js_code = js_code


	def __to_json__(self):
		return {'msgtype' : 'execute_js', 'js_code' : self.__js_code}


	@classmethod
	def __from_json__(cls, json):
		if json['msgtype'] == 'execute_js':
			return ExecuteJSMessage(json['js_code'])
		else:
			raise TypeError, 'msgtype is not execute_js'
