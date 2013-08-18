##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
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


