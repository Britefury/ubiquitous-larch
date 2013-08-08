##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.html import Html

def error_box(caption, contents):
	return Html('<div class="error_box"><span class="error_box_caption">{0}</span><br><div class="error_box_content">'.format(caption), contents, '</div></div>')

def horizontal_field(name, value):
	return Html('<span class="field_name">{0}</span><span class="field_value">'.format(name), value, '</span><br>')

def vertical_field(name, value):
	return Html('<span class="field_name">{0}</span><br><div class="field_value">'.format(name), value, '</div>')