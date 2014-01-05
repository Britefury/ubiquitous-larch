##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import webbrowser

from bottle import run

import ularch_cmdline
import ularch_bottle_app


if __name__ == '__main__':
	options = ularch_cmdline.parse_cmd_line()
	app = ularch_bottle_app.make_ularch_bottle_app(options.docpath, running_locally=True)
	print 'Point your browser at http://127.0.0.1:{0}/ to try The Ubiquitous Larch'.format(options.port)
	webbrowser.get().open('http://127.0.0.1:{0}/'.format(options.port))
	run(app, host='127.0.0.1', port=options.port)
