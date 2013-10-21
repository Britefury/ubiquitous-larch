try:
	from greenlet import greenlet, getcurrent, GreenletExit
except ImportError:
	coroutine = None
else:
	def coroutine(f):
		return greenlet(f)

	def terminate(co):
		co.throw(GreenletExit)

