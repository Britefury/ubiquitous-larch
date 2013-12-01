##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json


def _coerce_to_js_src_str(x, pres_ctx):
	if isinstance(x, JS):
		return x.build_js(pres_ctx)
	else:
		return json.dumps(x)


def _wrap_complex_expr_in_parens(expr, expr_src):
	if expr.__simple_js_expr__:
		return expr_src
	else:
		return '(' + expr_src + ')'

class JS (object):
	def build_js(self, pres_ctx):
		raise NotImplementedError, 'abstract'



class JSExpr (JS):
	__simple_js_expr__ = False


	def __call__(self, *args):
		return JSCall(self, args)

	def __getattr__(self, item):
		return JSGetProp(self, item)



class JSSimpleExpr (JSExpr):
	__simple_js_expr__ = True


class JSName (JSSimpleExpr):
	def __init__(self, name):
		self.__name = name

	def build_js(self, pres_ctx):
		return self.__name



class JSCall (JSExpr):
	def __init__(self, target, args):
		if isinstance(target, basestring):
			target = JSName(target)
		self.__target = target
		self.__args = tuple(args)


	def build_js(self, pres_ctx):
		target_src = _coerce_to_js_src_str(self.__target, pres_ctx)
		target_src = _wrap_complex_expr_in_parens(self.__target, target_src)
		args_srcs = [_coerce_to_js_src_str(a, pres_ctx)   for a in self.__args]
		return '{0}({1})'.format(target_src, ', '.join(args_srcs))


class JSGetProp (JSSimpleExpr):
	def __init__(self, target, prop_name):
		self.__target = target
		self.__prop_name = prop_name

	def build_js(self, pres_ctx):
		target_src = _coerce_to_js_src_str(self.__target, pres_ctx)
		return '{0}.{1}'.format(target_src, self.__prop_name)


class JSExprSrc (JSExpr):
	def __init__(self, src):
		self.__src = src


	def build_js(self, pres_ctx):
		return self.__src



name_node = JSName('node')

