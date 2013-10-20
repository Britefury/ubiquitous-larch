##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.util import coroutines


class Event (object):
	def __init__(self, page, segment, event_name, event_data):
		self.__page = page
		self.__segment = segment
		self.__event_name = event_name
		self.__event_data = event_data


	@property
	def page(self):
		return self.__page.public_api

	@property
	def fragment(self):
		if self.__segment is not None:
			return self.__segment.fragment
		else:
			inc_view = self.__page.inc_view
			if inc_view is not None:
				return inc_view.root_fragment_view
			else:
				return None

	@property
	def name(self):
		return self.__event_name

	@property
	def data(self):
		return self.__event_data




class AsyncApp (object):
	_app_stack = []

	def __init__(self, f, *args,** kwargs):
		self.__f = f
		self.__args = args
		self.__kwargs = kwargs
		self.__outer_co = None
		self.__co = None


	def go(self):
		self.__outer_co = coroutines.getcurrent()
		self.__co = coroutines.coroutine(self.__f)

		self._app_stack.append(self)
		self.__co.switch(*self.__args, **self.__kwargs)
		self._app_stack.pop()


	def enter(self, event):
		self.__co.switch(event)

	def leave(self):
		return self.__outer_co.switch()


	@classmethod
	def getcurrent(cls):
		return cls._app_stack[-1]   if len(cls._app_stack) > 0   else None




class EventHandler (object):
	def __init__(self):
		self._listeners = []
		self._children = []


	def connect(self, listener):
		self._notify_hook()
		self._listeners.append(listener)

	def disconnect(self, listener):
		self._listeners.remove(listener)
		self._notify_unhook()


	def __iadd__(self, listener):
		self.connect(listener)

	def __isub__(self, listener):
		self.disconnect(listener)


	def __call__(self, event):
		# Iterate over a copy
		for child in self._children[:]:
			if child(event):
				return True

		for child in self._listeners[:]:
			if child(event):
				return True


	def await(self):
		def handler(event):
			self.disconnect(handler)
			app.enter(event)


		app = AsyncApp.getcurrent()
		if app is None:
			raise RuntimeError, 'Cannot perform async wait; no async app is running'

		self.connect(handler)
		return app.leave()


	def _add_child(self, child):
		self._notify_hook()
		self._children.append(child)

	def _remove_child(self, child):
		self._children.remove(child)
		self._notify_unhook()


	def _has_output(self):
		return len(self._listeners) > 0  or  len(self._children) > 0



	def _notify_hook(self):
		pass

	def _notify_unhook(self):
		pass


	def filter(self, name_or_function):
		if isinstance(name_or_function, str)  or  isinstance(name_or_function, unicode):
			return EventHandlerFilterByName(self, name_or_function)
		else:
			return EventHandlerFilterByFunction(self, name_or_function)

	def join(self, event_handler):
		return EventHandlerJoin([self, event_handler])

	def __or__(self, event_handler):
		return self.join(event_handler)


class EventHandlerNode (EventHandler):
	def __init__(self, parents):
		super(EventHandlerNode, self).__init__()
		self._parents = parents


	def _notify_hook(self):
		if not self._has_output():
			for parent in self._parents:
				parent._add_child(self)

	def _notify_unhook(self):
		if not self._has_output():
			for parent in self._parents:
				parent._remove_child(self)



class EventHandlerFilterByName (EventHandlerNode):
	def __init__(self, parent, name):
		super(EventHandlerFilterByName, self).__init__([parent])
		self.__name = name


	def __call__(self, event):
		if event.name == self.__name:
			return super(EventHandlerFilterByName, self)(event)
		else:
			return False


class EventHandlerFilterByFunction (EventHandlerNode):
	def __init__(self, parent, filter_fn):
		super(EventHandlerFilterByFunction, self).__init__([parent])
		self.__filter_fn = filter_fn


	def __call__(self, event):
		if self.__filter_fn(event):
			return super(EventHandlerFilterByFunction, self)(event)
		else:
			return False



class EventHandlerJoin (EventHandlerNode):
	def join(self, event_handler):
		return EventHandlerJoin(self._parents + [event_handler])

