try:
	import greenlet
except ImportError:
	from _coroutines_pythreads import coroutine
else:
	from _coroutines_greenlet import coroutine

