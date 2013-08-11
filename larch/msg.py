##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************


def message(msgtype, **args):
	msg = {'msgtype': msgtype}
	msg.update(args)
	return msg
