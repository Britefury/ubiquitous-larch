try:
	import greenlet
except ImportError:
	coroutine = None
else:
	def coroutine(f):
		return greenlet.greenlet(f)
