##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************


class DocumentDependency (object):
	def __init__(self, url, deps=None):
		if deps is None:
			deps = []

		self._url = url
		self.__deps = deps


	@property
	def dependencies(self):
		return self.__deps


	def to_html(self):
		raise NotImplementedError, 'abstract'



class CSSDependency (DocumentDependency):
	def __init__(self, url, deps=None):
		super(CSSDependency, self).__init__(url, deps)

	def to_html(self):
		return '<link rel="stylesheet" type="text/css" href="{0}"/>'.format(self._url)



class JSDependency (DocumentDependency):
	def __init__(self, url, deps=None):
		super(JSDependency, self).__init__(url, deps)

	def to_html(self):
		return '<script type="text/javascript" src="{0}"></script>'.format(self._url)

