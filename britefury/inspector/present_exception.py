##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
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



def exc_box_to_html_src(caption, contents_str):
	return '<div class="error_box"><span class="error_box_caption">{0}</span><br><div class="error_box_content">{1}</div></div>'.format(caption, contents_str)


def exception_to_html_src(exc, tb):
	traceback_str = '<br>\n'.join(traceback.format_exc(tb).split('\n'))
	content = '<span class="exception_name">{0}</span><br><span class="exception_message">{0}</span><br><div class="exception_traceback">{0}</div>'.format(type(exc).__name__, exc.message, traceback_str)
	return exc_box_to_html_src('Exception', content)
