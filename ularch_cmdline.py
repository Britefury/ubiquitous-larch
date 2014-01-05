from optparse import OptionParser



class ULarchCmdlineOptions (object):
	def __init__(self, **attrs):
		self.__dict__.update(attrs)


def parse_cmd_line():
	usage = "usage: %prog [options] <documents_path>"
	parser = OptionParser(usage)
	parser.add_option('-p', '--port', dest='port', help='server port', type='int', default=5000)

	options, args = parser.parse_args()

	port = options.port
	docpath = args[0]   if len(args) > 0   else None

	return ULarchCmdlineOptions(port=port, docpath=docpath)


