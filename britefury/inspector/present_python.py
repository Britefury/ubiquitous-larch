##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
import inspect
import types

from britefury.pres.html import Html


def _span(css_class, x):
	return '<span class="{0}">{1}</span>'.format(css_class, x)


def _punct_html(x):
	return '<span class="pyprim_punctuation">{0}</span>'.format(x)

def _keyword(x):
	return '<span class="python_keyword">{0}</span>'.format(x)


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
_equals = _punct_html('=')




def present_class_header(x):
	bases = [_span('python_name', base.__name__)   for base in x.__bases__]
	return Html( '<p>' + _span('python_keyword', 'class') + ' ' + _span('python_classname', x.__name__) + ' ' + _open_paren + _comma_space.join(bases) + _close_paren + '</p>' )

def present_class(x):
	header = present_class_header(x)
	contents = [header]
	return Html(*contents)



def present_def_header(x):
	spec = inspect.getargspec(x)
	args = []
	for a in spec.args[:-len(spec.defaults)]:
		args.append(_span('python_name', a))
	for a, d in zip(spec.args[-len(spec.defaults):], spec.defaults):
		args.append(Html(*[_span('python_name', a) + _equals, d]))
	if spec.varargs is not None:
		args.append(_punct_html('*') + _span('python_name', spec.varargs))
	if spec.keywords is not None:
		args.append(_punct_html('**') + _span('python_name', spec.keywords))
	separated_args = []
	if len(args) > 0:
		separated_args.append(args[0])
		for a in args[1:]:
			separated_args.append(_comma_space)
			separated_args.append(a)

	return Html( *(['<p>' + _span('python_keyword', 'def') + ' ' + _span('python_defname', x.__name__) + ' ' + _open_paren] + separated_args + [_close_paren + '</p>']))

def present_function(x):
	header = present_def_header(x)
	contents = [header]
	return Html(*contents)




_present_fn_table = {
	type(type) : present_class,
	types.FunctionType : present_function,
}

def present_python(x):
	fn = _present_fn_table.get(type(x))
	if fn is not None:
		return fn(x)
	else:
		return None


