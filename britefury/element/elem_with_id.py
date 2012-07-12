##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.element.element import Element




class ElementWithId (Element):
	_unique_id_counter = 1


	def __init__(self):
		super(ElementWithId, self).__init__()
		self.__unique_id = ElementWithId._unique_id_counter
		ElementWithId._unique_id_counter += 1


	@property
	def element_id(self):
		return 'lch_element_' + str(self.__unique_id)
