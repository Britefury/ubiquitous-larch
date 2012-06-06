##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************
from britefury.message.message import Message


class ReplaceFragmentMessage (Message):
	def __init__(self, fragment_id, fragment_html):
		self.__fragment_id = fragment_id
		self.__fragment_html = fragment_html


	def __to_json__(self):
		return {'msgtype' : 'replace_fragment', 'frag_id' : self.__fragment_id, 'frag_content' : self.__fragment_html}


	@classmethod
	def __from_json__(cls, json):
		if json['msgtype'] == 'replace_fragment':
			return ReplaceFragmentMessage(json['frag_id'], json['frag_content'])
		else:
			raise TypeError, 'msgtype is not replace_fragment'
