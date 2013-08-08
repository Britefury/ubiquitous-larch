##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import sys
from collections import deque

from britefury.util.simple_attribute_table import SimpleAttributeTable
from britefury.pres.presctx import PresentationContext
from britefury.pres.pres import Pres
from britefury.pres.html import Html
from britefury.incremental import IncrementalMonitor, IncrementalFunctionMonitor
from britefury.inspector.present_exception import present_exception_with_traceback
from britefury.dynamicpage.segment import  HtmlContent




def _exception_during_presentation(exc_pres):
	return Html('<div class="exception_during_presentation"><span class="exception_during_pres_title">Exception during presentation</span>', exc_pres, '</div>')

def _exception_during_presentation_to_html(exc_pres):
	return Html('<div class="exception_during_presentation"><span class="exception_during_pres_title">Exception while converting presentation to HTML</span>', exc_pres, '</div>')



class _FragmentView (object):
	_FLAG_SUBTREE_REFRESH_REQUIRED = 0x1
	_FLAG_NODE_REFRESH_REQUIRED = 0x2
	_FLAG_NODE_REFRESH_IN_PROGRESS = 0x4
	_FLAG_DISABLE_INSPECTOR = 0x8

	_FLAG_REFSTATE_MULTIPLIER_ = 0x10
	_FLAG_REFSTATE_NONE = 0x0 * _FLAG_REFSTATE_MULTIPLIER_
	_FLAG_REFSTATE_REFED = 0x1 * _FLAG_REFSTATE_MULTIPLIER_
	_FLAG_REFSTATE_UNREFED = 0x2 * _FLAG_REFSTATE_MULTIPLIER_
	_FLAG_REFSTATEMASK_ = 0x3 * _FLAG_REFSTATE_MULTIPLIER_

	_FLAGS_FRAGMENTVIEW_END = 0x4 * _FLAG_REFSTATE_MULTIPLIER_


	def __init__(self, model, inc_view):
		self.__flags = 0

		self.__set_flag(self._FLAG_SUBTREE_REFRESH_REQUIRED)
		self.__set_flag(self._FLAG_NODE_REFRESH_REQUIRED)

		self.__inc_view = inc_view
		self.__model = model

		self.__parent = None
		self.__next_sibling = None
		self.__children_head = None
		self.__children_tail = None

		self.__fragment_factory = None
		self.__incr = IncrementalFunctionMonitor(self)
		self.__incr.add_listener(self.__on_incremental_monitor_changed)

		# Segments
		self.__segment = self.__inc_view.dynamic_page.new_segment(desc='{0}'.format(type(self.__model).__name__), owner=self)
		self.__sub_segments = []

		# Resources
		self.__resources = []


	def _dispose(self):
		self.__incr.remove_listener(self.__on_incremental_monitor_changed)
		for rsc in self.__resources:
			self.__inc_view.dynamic_page.unref_resource(rsc)
		for sub_seg in self.__sub_segments:
			self.__inc_view.dynamic_page.remove_segment(sub_seg)
		self.__inc_view.dynamic_page.remove_segment(self.__segment)



	#
	#
	# Segment acquisition
	#
	#

	@property
	def __segment_reference(self):
		"""
		Get a reference to the segment that corresponds to this fragment

		Called from present_inner_fragment, which is called while conerting an InnerFragment Pres to HtmlContent
		"""
		return self.__segment.reference()

	@property
	def _refreshed_segment_reference(self):
		self.refresh()
		return self.__segment.reference()



	def disable_inspector(self):
		self.__set_flag(self._FLAG_DISABLE_INSPECTOR)



	@property
	def is_active(self):
		return self.__parent is not None



	#
	#
	# Structure / model
	#
	#

	@property
	def view(self):
		return self.__inc_view

	@property
	def page(self):
		return self.__inc_view.dynamic_page.public_api

	@property
	def parent(self):
		return self.__parent

	@property
	def children(self):
		c = self.__children_head
		while c is not None:
			yield c
			c = c.__next_sibling

	@property
	def model(self):
		return self.__model


	def compute_subtree_size(self):
		size = 1
		for c in self.children:
			size += c.compute_subtree_size()
		return size



	#
	#
	# Context
	#
	#

	@property
	def dynamic_page(self):
		return self.__inc_view.dynamic_page

	@property
	def service(self):
		return self.__inc_view.service

	@property
	def subject(self):
		return self.__inc_view.subject

	@property
	def perspective(self):
		return self.fragment_factory.perspective

	def create_presentation_context(self):
		f = self.fragment_factory
		return PresentationContext(self, f.perspective, f.inherited_state)



	#
	#
	# Sub-segments
	#
	#

	def create_sub_segment(self, content):
		sub_seg = self.__inc_view.dynamic_page.new_segment(content, desc='subseg_{0}'.format(type(self.__model).__name__), owner=self)
		self.__sub_segments.append(sub_seg)
		return sub_seg



	def create_resource(self, rsc_data, context):
		page_rsc = self.__inc_view.dynamic_page.resource_for(rsc_data, context)
		self.__resources.append(page_rsc)
		return page_rsc



	#
	#
	# Fragment factory
	#
	#

	@property
	def fragment_factory(self):
		return self.__fragment_factory


	@fragment_factory.setter
	def fragment_factory(self, f):
		if f is not self.__fragment_factory:
			self.__fragment_factory = f
			self.__incr.on_changed()




	#
	#
	# Refresh
	#
	#

	def refresh(self):
		if self.__test_flag(self._FLAG_SUBTREE_REFRESH_REQUIRED):
			self.__refresh_subtree()
			self.__clear_flag(self._FLAG_SUBTREE_REFRESH_REQUIRED)


	def queue_refresh(self):
		self.__incr.on_changed()


	def disable_auto_refresh(self):
		self.__incr.block_and_clear_incoming_dependencies()



	def __refresh_subtree(self):
		self.__set_flag(self._FLAG_NODE_REFRESH_IN_PROGRESS)

		content = self.__segment.content
		self.__inc_view.on_fragment_content_change_from(self, content)

		if self.__test_flag(self._FLAG_NODE_REFRESH_REQUIRED):
			# Compute result for this fragment, and refresh all children
			refresh_state = self.__incr.on_refresh_begin()
			if refresh_state is not None:
				content = self.__compute_fragment_content()
			self.__incr.on_refresh_end(refresh_state)

		# Refresh each child
		child = self.__children_head
		while child is not None:
			child.refresh()
			child = child.__next_sibling

		if self.__test_flag(self._FLAG_NODE_REFRESH_REQUIRED):
			self.__incr.on_access()
			# Set the content
			self.__segment.content = content

		self.__inc_view.on_fragment_content_change_to(self, content)
		self.__clear_flag(self._FLAG_NODE_REFRESH_REQUIRED)
		self.__clear_flag(self._FLAG_NODE_REFRESH_IN_PROGRESS)


	@staticmethod
	def __unref_subtree(inc_view, fragment):
		q = deque()

		q.append(fragment)

		while len(q) > 0:
			f = q.popleft()

			if f.__ref_state != _FragmentView._FLAG_REFSTATE_UNREFED:
				inc_view._node_table._unref_fragment_view(f)

				child = f.__children_head
				while child is not None:
					q.append(child)
					child = child.__next_sibling



	@staticmethod
	def __ref_subtree(inc_view, fragment):
		q = deque()

		q.append(fragment)

		while len(q) > 0:
			f = q.popleft()

			if f.__ref_state != _FragmentView._FLAG_REFSTATE_REFED:
				inc_view._node_table._ref_fragment_view(f)

				child = f.__children_head
				while child is not None:
					q.append(child)
					child = child.__next_sibling



	def __child_disconnected(self):
		# ONLY INVOKE AGAINST A FRAGMENT WHICH HAS BEEN UNREFED, AND DURING A REFRESH

		# Clear the links between fragments
		child = self.__children_head
		while child is not None:
			next = child.__next_sibling

			child.__parent = None
			child.__next_sibling = None

			child = next
		self.__children_head = self.__children_tail = None

		if not self.__test_flag(self._FLAG_NODE_REFRESH_REQUIRED):
			self.__set_flag(self._FLAG_NODE_REFRESH_REQUIRED)
			self.__request_subtree_refresh()



	def __compute_fragment_content(self):
		# Clear the existing content
		self._clear_existing_content()

		# Generate new content
		self.__on_compute_node_result_begin()
		self.__clear_flag(self._FLAG_DISABLE_INSPECTOR)

		content = None
		try:
			if self.__fragment_factory is not None:
				content = self.__fragment_factory.build_html_content_for_fragment(self.__inc_view, self, self.__model)   if self.__fragment_factory is not None   else None
		finally:
			self.__on_compute_node_result_end()
		return content


	def _clear_existing_content(self):
		# Unregister existing child relationships
		child = self.__children_head
		while child is not None:
			next = child.__next_sibling

			_FragmentView.__unref_subtree(self.__inc_view, child)
			child.__parent = None
			child.__next_sibling = None

			child = next
		self.__children_head = self.__children_tail = None

		# Remove sub segments
		for sub_seg in self.__sub_segments:
			self.__inc_view.dynamic_page.remove_segment(sub_seg)
		del self.__sub_segments[:]



	#
	#
	# Child / parent relationship
	#
	#

	def __register_child(self, child):
		if child.__parent is not None  and  child.parent is not self:
			child.__parent.__child_disconnected()

		# Append child to the list of children
		if self.__children_tail is not None:
			self.__children_tail.__next_sibling = child

		if self.__children_head is None:
			self.__children_head = child

		self.__children_tail = child

		child.__parent = self

		# Ref the subtree, so that it is kept around
		_FragmentView.__ref_subtree(self.__inc_view, child)



	#
	#
	# Child notifications
	#
	#

	def __request_subtree_refresh(self):
		if not self.__test_flag(self._FLAG_SUBTREE_REFRESH_REQUIRED):
			self.__set_flag(self._FLAG_SUBTREE_REFRESH_REQUIRED)
			if self.__parent is not None:
				self.__parent.__request_subtree_refresh()

			self.__inc_view._on_node_request_refresh(self)



	#
	#
	# Refresh methods
	#
	#

	def __on_compute_node_result_begin(self):
		pass

	def __on_compute_node_result_end(self):
		pass





	#
	#
	# Inner fragment presentation
	#
	#

	def present_inner_fragment(self, model, perspective, inherited_state, subject=None):
		if subject is None:
			subject = self.__fragment_factory._subject

		if inherited_state is None:
			raise ValueError, 'inherited_state is None'

		child_fragment_view = self.__inc_view._build_fragment_view(model, self.__inc_view._get_unique_fragment_factory(perspective, subject, inherited_state))

		# Register the parent <-> child relationship before refreshing the node, so that the relationship is 'available' during (re-computation)
		self.__register_child(child_fragment_view)

		# We don't need to refresh the child node - this is done by incremental view after the fragments contents have been computed

		# If a refresh is in progress, we do not need to refresh the child node, as all child nodes will be refreshed by FragmentView.refreshSubtree()
		# Otherwise, we are constructing a presentation of a child node, outside the normal process, in which case, a refresh is required.
		if not self.__test_flag(self._FLAG_NODE_REFRESH_IN_PROGRESS):
			# Block access tracking to prevent the contents of this node being dependent upon the child node being refreshed,
			# and refresh the view node
			# Refreshing the child node will ensure that when its contents are inserted into outer elements, its full element tree
			# is up to date and available.
			# Blocking the access tracking prevents an inner node from causing all parent/grandparent/etc nodes from requiring a
			# refresh.
			current = IncrementalMonitor.block_access_tracking()
			child_fragment_view.refresh()
			IncrementalMonitor.unblock_access_tracking(current)

		return HtmlContent([child_fragment_view.__segment_reference])





	#
	#
	# Incremental monitor notifications
	#
	#

	def __on_incremental_monitor_changed(self, incr):
		if not self.__test_flag(self._FLAG_NODE_REFRESH_REQUIRED):
			self.__set_flag(self._FLAG_NODE_REFRESH_REQUIRED)
			self.__request_subtree_refresh()






	#
	#
	# Flags
	#
	#

	def __clear_flag(self, flag):
		self.__flags &= ~flag


	def __set_flag(self, flag):
		self.__flags |= flag


	def __set_flag_value(self, flag, value):
		if value:
			self.__flags |= flag
		else:
			self.__flags &= ~flag


	def __test_flag(self, flag):
		return (self.__flags & flag) != 0


	@property
	def __ref_state(self):
		return self.__flags & self._FLAG_REFSTATEMASK_

	@__ref_state.setter
	def __ref_state(self, state):
		self.__flags = (self.__flags & ~self._FLAG_REFSTATEMASK_) | state

	def _set_ref_state_refed(self):
		self.__ref_state = self._FLAG_REFSTATE_REFED

	def _set_ref_state_unrefed(self):
		self.__ref_state = self._FLAG_REFSTATE_UNREFED



class FragmentFactory (object):
	def __init__(self, inc_view, perspective, subject, inherited_state):
		self.__perspective = perspective
		self.__subject = subject
		self.__inherited_state = inherited_state
		self.__hash = hash((id(perspective), hash(inherited_state), hash(id(subject))))


	@property
	def _subject(self):
		return self.__subject


	def __hash__(self):
		return self.__hash

	def __eq__(self, other):
		if isinstance(other, FragmentFactory):
			return other.__perspective is self.__perspective  and  other.__subject is self.__subject  and  other.__inherited_state is self.__inherited_state
		else:
			return NotImplemented

	def __ne__(self, other):
		if isinstance(other, FragmentFactory):
			return other.__perspective is not self.__perspective  or  other.__subject is not self.__subject  or  other.__inherited_state is not self.__inherited_state
		else:
			return NotImplemented


	def build_html_content_for_fragment(self, inc_view, fragment_view, model):
		# Create the view fragment
		try:
			fragment_pres = self.__perspective.present_object(model, fragment_view)
		except Exception, e:
			fragment_pres = _exception_during_presentation(present_exception_with_traceback(e, sys.exc_info()[2]))

		try:
			if not isinstance(fragment_pres, Pres):
				raise TypeError, 'Presentation functions must return an object of type Pres, an object of type {0} was received'.format(type(fragment_pres).__name__)
		except Exception, e:
			fragment_pres = _exception_during_presentation(present_exception_with_traceback(e, sys.exc_info()[2]))

		try:
			html_content = self.__pres_to_html_content(fragment_pres, fragment_view)
		except Exception, e:
			# The HTML content may have been partially built before the exception was raised, in which case fragment view nodes - and
			# their respective segments - may have been created. They are now orphaned and need to be disposed of
			fragment_view._clear_existing_content()
			fragment_pres = _exception_during_presentation_to_html(present_exception_with_traceback(e, sys.exc_info()[2]))
			html_content = self.__pres_to_html_content(fragment_pres, fragment_view)

		return html_content


	def __pres_to_html_content(self, fragment_pres, fragment_view):
		return fragment_pres.build(PresentationContext(fragment_view, self.__perspective, self.__inherited_state))



class _TableForModel (object):
	def __init__(self, table, model):
		self.__table = table
		self.__model = model

		self.__refed_fragment_views = set()
		self.__unrefed_fragment_views = None


	def __add_unrefed_fragment_view(self, v):
		if self.__unrefed_fragment_views is None:
			self.__unrefed_fragment_views = set()
		self.__unrefed_fragment_views.add(v)

	def __remove_unrefed_fragment_view(self, v):
		if self.__unrefed_fragment_views is not None:
			self.__unrefed_fragment_views.remove(v)
			if len(self.__unrefed_fragment_views) == 0:
				self.__unrefed_fragment_views = None


	def _get_unrefed_fragment_view_for(self, fragment_factory):
		if self.__unrefed_fragment_views is not None:
			for v in self.__unrefed_fragment_views:
				if v.fragment_factory == fragment_factory:
					return v
		return None


	@property
	def refed_fragment_views(self):
		return self.__refed_fragment_views

	def __len__(self):
		return len(self.__refed_fragment_views)

	@property
	def num_unrefed_fragment_views(self):
		return len(self.__unrefed_fragment_views)   if self.__unrefed_fragment_views is not None   else 0


	def ref_fragment_view(self, v):
		self.__remove_unrefed_fragment_view(v)
		self.__refed_fragment_views.add(v)

	def unref_fragment_view(self, v):
		self.__refed_fragment_views.remove(v)
		self.__add_unrefed_fragment_view(v)


	def _clean(self):
		self.__unrefed_fragment_views = None
		if len(self.__refed_fragment_views) == 0:
			self.__table._remove_view_table_for_model(self.__model)



class IncrementalViewTable (object):
	def __init__(self):
		self.__table = {}
		self.__unrefed_fragment_views = set()


	def get_unrefed_fragment_for_model(self, model, fragment_factory):
		try:
			sub_table = self.__table[id(model)]
		except KeyError:
			return None
		return sub_table._get_unrefed_fragment_view_for(fragment_factory)


	def get(self, model):
		try:
			sub_table = self.__table[id(model)]
		except KeyError:
			return []
		return sub_table.refed_fragment_views


	def __contains__(self, model):
		return self.get_num_fragments_for_model(model) > 0


	def __len__(self):
		size = 0
		for v in self.__table.values():
			size += len(v)
		return size


	@property
	def num_models(self):
		return len(self.__table)


	def get_num_fragments_for_model(self, model):
		try:
			sub_table = self.__table[id(model)]
		except KeyError:
			return None
		return len(sub_table)


	def get_num_unrefed_fragments_for_model(self, model):
		try:
			sub_table = self.__table[id(model)]
		except KeyError:
			return None
		return sub_table.num_unrefed_fragment_views


	def clean(self):
		# We need to remove all nodes within the sub-trees rooted at the unrefed nodes
		unrefed_stack = []
		unrefed_stack.extend(self.__unrefed_fragment_views)

		while len(unrefed_stack) > 0:
			fragment_view = unrefed_stack.pop()

			# Don't need to visit children; entire sub-trees are 'unrefed' all at once

			try:
				sub_table = self.__table[id(fragment_view.model)]
			except KeyError:
				pass
			else:
				sub_table._clean()

			fragment_view._dispose()

		self.__unrefed_fragment_views.clear()


	def _ref_fragment_view(self, fragment_view):
		fragment_view._set_ref_state_refed()
		model = fragment_view.model
		try:
			sub_table = self.__table[id(model)]
		except KeyError:
			sub_table = _TableForModel(self, model)
			self.__table[id(model)] = sub_table
		sub_table.ref_fragment_view(fragment_view)
		try:
			self.__unrefed_fragment_views.remove(fragment_view)
		except KeyError:
			pass


	def _unref_fragment_view(self, fragment_view):
		fragment_view._set_ref_state_unrefed()
		model = fragment_view.model
		try:
			sub_table = self.__table[id(model)]
		except KeyError:
			sub_table = _TableForModel(self, model)
			self.__table[id(model)] = sub_table
		sub_table.unref_fragment_view(fragment_view)
		self.__unrefed_fragment_views.add(fragment_view)


	def _remove_view_table_for_model(self, model):
		del self.__table[id(model)]





class IncrementalView (object):
	def __init__(self, subject, dynamic_page):
		self.__subject = subject

		self.__root_model = subject.focus
		self._root_perspective = subject.perspective
		self.__root_fragment_view = None
		self.__root_fragment_factory = None


		self._node_table = IncrementalViewTable()
		self.__refresh_required = False

		self.__unique_fragment_factories = {}

		self.__dynamic_page = dynamic_page
		title = subject.title
		if title is not None:
			self.__dynamic_page.title = title

		self.__lock = None

		self.__initialise()




	#
	#
	# View, model, subject
	#
	#

	@property
	def root_model(self):
		return self.__root_model

	@property
	def subject(self):
		return self.__subject

	@property
	def dynamic_page(self):
		return self.__dynamic_page

	@property
	def service(self):
		return self.__dynamic_page.service




	#
	#
	# Initialisation
	#
	#

	def __initialise(self):
		# Create and set the root fragment fragment factory
		fragment_factory = self._get_unique_fragment_factory(self._root_perspective, self.__subject, SimpleAttributeTable.instance)
		self._set_root_fragment_factory(fragment_factory)

		# Refresh
		self._refresh()

		# Get the root fragment
		root_frag_view = self._get_root_fragment_view()
		# Set the content of the dynamic page to the content of the root fragment
		self.__dynamic_page.root_segment = root_frag_view._refreshed_segment_reference


	#
	#
	# Refreshing
	#
	#

	def _refresh(self):
		if self.__refresh_required:
			self.__refresh_required = False
			self.__perform_refresh()


	def _queue_refresh(self):
		if not self.__refresh_required:
			self.__refresh_required = True
			self.__dynamic_page.queue_task(self._refresh)



	def _on_node_request_refresh(self, fragment_view):
		if fragment_view is self.__root_fragment_view:
			self._queue_refresh()



	def __perform_refresh(self):
		self.__on_view_refresh_begin()
		root_frag = self._get_root_fragment_view()
		if root_frag is not None:
			root_frag.refresh()
		self._node_table.clean()
		self.__on_view_refresh_end()



	def __on_view_refresh_begin(self):
		pass

	def __on_view_refresh_end(self):
		pass



	#
	#
	# Fragment building and acquisition
	#
	#

	def _get_root_fragment_view(self):
		if self.__root_fragment_factory is None:
			raise ValueError, 'No root fragment factory set'

		if self.__root_fragment_view is not None:
			self._node_table._unref_fragment_view(self.__root_fragment_view)
		if self.__root_fragment_view is None:
			self.__root_fragment_view = self._build_fragment_view(self.__root_model, self.__root_fragment_factory)
		if self.__root_fragment_view is not None:
			self._node_table._ref_fragment_view(self.__root_fragment_view)
		return self.__root_fragment_view


	def _build_fragment_view(self, model, fragment_factory):
		# Try asking the table for an unused fragment view for the model
		fragment_view = self._node_table.get_unrefed_fragment_for_model(model, fragment_factory)

		if fragment_view is None:
			# No existing incremental tree node could be acquired.
			# Create a new one and add it to the table
			fragment_view = _FragmentView(model, self)

		fragment_view.fragment_factory = fragment_factory

		return fragment_view


	#
	#
	# Fragment factories
	#
	#

	def _set_root_fragment_factory(self, fragment_factory):
		if fragment_factory is not self.__root_fragment_factory:
			self.__root_fragment_factory = fragment_factory
			self._queue_refresh()


	def _get_unique_fragment_factory(self, perspective, subject, inherited_state):
		factory = FragmentFactory(self, perspective, subject, inherited_state)
		try:
			return self.__unique_fragment_factories[factory]
		except KeyError:
			self.__unique_fragment_factories[factory] = factory
			return factory



	def on_fragment_content_change_from(self, fragment_view, content):
		pass


	def on_fragment_content_change_to(self, fragment_view, content):
		pass