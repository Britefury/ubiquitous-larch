##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html

def error_box(caption, contents):
	return Html('<div class="error_box"><span class="error_box_caption">{0}</span><br><div class="error_box_content">'.format(caption), contents, '</div></div>')