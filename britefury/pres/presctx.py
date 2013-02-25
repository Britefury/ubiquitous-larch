##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************


class PresentationContext (object):
	def __init__(self, fragment_view, perspective, inherited_state):
		self.__fragment_view = fragment_view
		self.__perspective = perspective
		self.__inherited_state = inherited_state



	@property
	def fragment_view(self):
		return self.__fragment_view

	@property
	def perspective(self):
		return self.__perspective

	@property
	def inherited_state(self):
		return self.__inherited_state

	@property
	def subject(self):
		return self.__fragment_view.subject   if self.__fragment_view is not None   else None




