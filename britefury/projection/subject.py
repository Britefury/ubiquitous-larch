##-*************************
##-* This program is free software; you can use it, redistribute it and/or modify it
##-* under the terms of the GNU General Public License version 2 as published by the
##-* Free Software Foundation. The full text of the GNU General Public License
##-* version 2 can be found in the file named 'COPYING' that accompanies this
##-* program. This source code is (C)copyright Geoffrey French 1999-2012.
##-*************************
from britefury.attribute_table.simple_attribute_table import SimpleAttributeTable
from britefury.default_perspective.default_perspective import DefaultPerspective


class Subject (object):
	def __init__(self, focus, perspective=DefaultPerspective.instance, subject_context=SimpleAttributeTable.instance, stylesheet_names=[], script_names=[]):
		self.__focus = focus
		self.__perspective = perspective
		self.__subject_context = subject_context
		self.__stylesheet_names = stylesheet_names
		self.__script_names = script_names


	@property
	def focus(self):
		return self.__focus

	@property
	def perspective(self):
		return self.__perspective

	@property
	def subject_context(self):
		return self.__subject_context

	@property
	def stylesheet_names(self):
		return self.__stylesheet_names

	@property
	def script_names(self):
		return self.__script_names