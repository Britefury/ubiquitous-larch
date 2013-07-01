##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
__author__ = 'Geoff'



class DynamicSegment (object):
	"""A dynamic segment

	Represents a segment of HTML content. Its contents is stored in an HtmlContent object.

	Segments can be nested via references; create a reference using the reference() method and put it into the content of a parent segment to nest this within a parent segment.
	"""
	def __init__(self, doc, seg_id, content=None):
		self.__doc = doc
		self.__id = seg_id
		assert content is None  or  isinstance(content, HtmlContent)
		self.__content = content
		self.__parent = None
		self.__event_handlers = None
		self.__initialise_scripts = None
		self.__shutdown_scripts = None
		self.__connect_children()


	@property
	def id(self):
		"""The segment ID
		"""
		return self.__id

	@property
	def parent(self):
		"""The parent segment
		"""
		return self.__parent


	@property
	def document(self):
		return self.__doc


	@property
	def content(self):
		"""The content. Must be either None or an HtmlContent instance.
		"""
		return self.__content

	@content.setter
	def content(self, x):
		if x is not None  and not  isinstance(x, HtmlContent):
			raise TypeError, 'Content should be either None or an HtmlContent instance'
		self.__disconnect_children()
		self.__content = x
		self.__connect_children()
		self.__doc._table._segment_modified(self, x)


	def reference(self):
		"""Create a reference to this segment.
		"""
		return SegmentRef(self)



	# Event handling
	def add_event_handler(self, handler):
		"""Register an event handler
		"""
		if self.__event_handlers is None:
			self.__event_handlers = []
		self.__event_handlers.append(handler)


	def _handle_event(self, event_name, ev_data):
		if self.__event_handlers is not None:
			for handler in self.__event_handlers:
				if handler(event_name, ev_data):
					return True
		return False


	# Initialisation
	def get_initialise_scripts(self):
		return self.__initialise_scripts


	def add_initialise_script(self, initialiser):
		"""Add an initialiser
		"""
		if self.__initialise_scripts is None:
			self.__initialise_scripts = []
		self.__initialise_scripts.append(initialiser)



	# Shutdown
	def get_shutdown_scripts(self):
		return self.__initialise_scripts


	def add_shutdown_script(self, script):
		"""Add a shutdown script
		"""
		if self.__shutdown_scripts is None:
			self.__shutdown_scripts = []
		self.__shutdown_scripts.append(script)



	# HTML generation
	def _place_holder(self):
		return '<span class="__lch_seg_placeholder" data-larchsegid="{0}"></span>'.format(self.__id)

	def _inline_html(self, ref_resolver):
		items = []
		self._build_inline_html(items, ref_resolver)
		return ''.join(items)

	def _build_inline_html(self, items, ref_resolver):
		items.append('<span class="__lch_seg_begin" data-larchsegid="{0}"></span>'.format(self.__id))
		if self.__content is not None:
			self.__content._build_html(items, ref_resolver)
		items.append('<span class="__lch_seg_end" data-larchsegid="{0}"></span>'.format(self.__id))



	def __connect_children(self):
		if self.__content is not None:
			self.__connect_children_in_content(self.__content)


	def __disconnect_children(self):
		if self.__content is not None:
			self.__disconnect_children_in_content(self.__content)



	def __connect_children_in_content(self, content):
		for x in content:
			if isinstance(x, str)  or  isinstance(x, unicode):
				continue
			elif isinstance(x, SegmentRef):
				seg = x.segment
				seg.__parent = self
			elif isinstance(x, HtmlContent):
				self.__connect_children_in_content(x)
			else:
				raise TypeError, 'contents of HtmlContent should be str, unicode, SegmentRef or HtmlContent'

	def __disconnect_children_in_content(self, content):
		for x in content:
			if isinstance(x, str)  or  isinstance(x, unicode):
				continue
			elif isinstance(x, SegmentRef):
				seg = x.segment
				seg.__parent = None
			elif isinstance(x, HtmlContent):
				self.__disconnect_children_in_content(x)
			else:
				raise TypeError, 'contents of HtmlContent should be str, unicode, SegmentRef or HtmlContent'






class SegmentRef (object):
	"""A reference to a segment. Put these in HtmlContent objects to nest segments.
	"""
	def __init__(self, segment):
		assert isinstance(segment, DynamicSegment)
		self.__segment = segment


	@property
	def segment(self):
		return self.__segment

	def _build_html(self, items, ref_resolver=None):
		if ref_resolver is not None:
			ref_resolver(items, self.__segment)
		else:
			items.append(self.__segment._place_holder())


	def _complete_html(self):
		"""Build the HTML content of the complete segment subtree rooted at the segment pointed to by this reference
		"""
		items = []
		self._build_html(items, self.__resolve_complete)
		return ''.join(items)


	def __resolve_complete(self, items, seg):
		return seg._build_inline_html(items, self.__resolve_complete)







class HtmlContent (list):
	"""HTML Content

	Used to represent the HTML content of a dynamic segment.

	It is a sequence of items, each of which can be a string/unicode, a SegmentRef or an HtmlContent.
	"""
	def __init__(self, contents):
		for x in contents:
			assert isinstance(x, str)  or  isinstance(x, unicode)  or  isinstance(x, SegmentRef)  or  isinstance(x, HtmlContent)
		super(HtmlContent, self).__init__(contents)


	def _build_html(self, items, ref_resolver=None):
		"""Generate the HTML source represented by this HtmlContent instance.
		"""
		for x in self:
			if isinstance(x, str)  or  isinstance(x, unicode):
				items.append(x)
			else:
				x._build_html(items, ref_resolver)
