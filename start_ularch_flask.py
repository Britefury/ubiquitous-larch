##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import tempfile, os, webbrowser

from flask import Flask, request, Response, abort, redirect
from larch.core.dynamicpage.service import UploadedFile
from larch.core.projection_service import CouldNotResolveLocationError

import ularch_cmdline, ularch_flask_app



if __name__ == '__main__':
	options = ularch_cmdline.parse_cmd_line()
	app = ularch_flask_app.make_ularch_flask_app(options.docpath, running_locally=True)
	print 'Point your browser at http://127.0.0.1:{0}/ to try The Ubiquitous Larch'.format(options.port)
	webbrowser.get().open('http://127.0.0.1:{0}/'.format(options.port))
	app.run(debug=False, port=options.port)
