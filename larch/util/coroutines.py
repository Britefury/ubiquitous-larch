##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************

try:
	import greenlet
except ImportError:
	from _coroutines_pythreads import coroutine, getcurrent, terminate as terminate_coroutine
else:
	from _coroutines_greenlet import coroutine, getcurrent, terminate as terminate_coroutine

