##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
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
	def subject_context(self):
		return self.__fragment_view.subject_context   if self.__fragment_view is not None   else None




