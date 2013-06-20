##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from britefury.projection.subject import Subject




class ProjectSubject (Subject):
	def __init__(self, enclosing_subject, location_trail, project, perspective=None):
		super(ProjectSubject, self).__init__(enclosing_subject, location_trail, project, perspective, title='Project')


	def __resolve__(self, name):
		return self.focus.root.__subject__(self, [name], self.perspective).__resolve__(name)



class ContainerSubject (Subject):
	def __init__(self, enclosing_subject, location_trail, package, perspective=None, title=''):
		super(ContainerSubject, self).__init__(enclosing_subject, location_trail, package, perspective, title=title)


	def __resolve__(self, name):
		contents_map = self.focus.contents_map
		if name in contents_map:
			return contents_map[name].__subject__(self, [name], self.perspective)



class PackageSubject (ContainerSubject):
	def __init__(self, enclosing_subject, location_trail, package, perspective=None):
		super(ContainerSubject, self).__init__(enclosing_subject, location_trail, package, perspective, title=package.name)



class RootSubject (ContainerSubject):
	def __init__(self, enclosing_subject, location_trail, package, perspective=None):
		super(ContainerSubject, self).__init__(enclosing_subject, location_trail, package, perspective, title='Index')
