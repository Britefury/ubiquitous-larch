##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************


class Message (object):
	def __to_json__(self):
		raise NotImplementedError, 'abstract'


	@classmethod
	def __from_json__(cls, json):
		raise NotImplementedError, 'abstract'