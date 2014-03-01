##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************

try:
	from greenlet import greenlet, getcurrent, GreenletExit
except ImportError:
	coroutine = None
else:
	def coroutine(f):
		return greenlet(f)

	def terminate(co):
		co.throw(GreenletExit)

