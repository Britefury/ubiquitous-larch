try:
	import greenlet
except ImportError:
	from _coroutines_pythreads import coroutine, getcurrent, terminate as terminate_coroutine
else:
	from _coroutines_greenlet import coroutine, getcurrent, terminate as terminate_coroutine

