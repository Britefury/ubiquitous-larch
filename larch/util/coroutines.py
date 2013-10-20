try:
	import greenlet
except ImportError:
	from _coroutines_pythreads import coroutine, getcurrent
else:
	from _coroutines_greenlet import coroutine, getcurrent

