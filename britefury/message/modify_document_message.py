##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.message.message import Message


class ModifyDocumentMessage (Message):
	def __init__(self, changes):
		self.__changes = changes


	def __to_json__(self):
		return {'msgtype' : 'modify_document', 'changes' : self.__changes}


	@classmethod
	def __from_json__(cls, json):
		if json['msgtype'] == 'modify_document':
			return ModifyDocumentMessage(json['changes'])
		else:
			raise TypeError, 'msgtype is not modify_document'
