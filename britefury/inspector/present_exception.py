##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import traceback

from britefury.pres.obj_pres import error_box
from britefury.pres.html import Html




def present_exception_no_traceback(exc):
	content = Html('<span class="exception_name">{0}</span>'.format(type(exc).__name__), '<br>',
		       '<span class="exception_message">{0}</span>'.format(exc.message))
	return error_box('Exception', content)


def present_exception(exc, tb):
	traceback_str = '<br>\n'.join(traceback.format_exc(tb).split('\n'))
	content = Html('<span class="exception_name">{0}</span>'.format(type(exc).__name__), '<br>',
		       '<span class="exception_message">{0}</span>'.format(exc.message), '<br>',
		       '<div class="exception_traceback">{0}</div>'.format(traceback_str))
	return error_box('Exception', content)
