try:
	from greenlet import greenlet, getcurrent
except ImportError:
	coroutine = None
else:
	def coroutine(f):
		return greenlet(f)
