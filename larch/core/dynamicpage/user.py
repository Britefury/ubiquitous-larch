##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
##-*************************



class User (object):
	"""
	Base user object
	"""

	def __init__(self, user_id, username):
		"""
		Constructor

		:param user_id: The user ID
		:param username: The username
		:return: User instance
		"""
		self.__user_id = user_id
		self.__username = username


	@property
	def user_id(self):
		return self.__user_id


	@property
	def username(self):
		return self.__username


