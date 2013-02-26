##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.pres.html import Html


def _punct_html(x):
	return '<span class="pyprim_punctuation">{0}</span>'.format(x)



_quote = _punct_html('"')
_triple_quote = _punct_html('"""')


_open_paren = _punct_html('(')
_close_paren = _punct_html(')')
_open_bracket = _punct_html('[')
_close_bracket = _punct_html(']')
_open_brace = _punct_html('{')
_close_brace = _punct_html('}')
_comma = _punct_html(',')
_comma_space = _punct_html(',') + ' '
_colon = _punct_html(':')
_plus = _punct_html('+')



def present_type(x):
	header = '<p>class {0}</p>'.format(x.__name__)
	contents = [header]
	return Html(*contents)




_present_fn_table = {
type(type) : present_type,
}

def present_python(x):
	fn = _present_fn_table.get(type(x))
	if fn is not None:
		return fn(x)
	else:
		return None


