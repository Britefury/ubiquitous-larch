##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2012.
##-*************************
from britefury.projection.abstract_perspective import AbstractPerspective
from britefury.inspector.present_primitive import present_primitive_data, is_small_primitive_data, present_string
from britefury.pres.controls.expander import dropdown_expander
from britefury.pres.obj_pres import horizontal_field, vertical_field
from britefury.pres.html import Html
from britefury.pres.pres import Pres



def _field(name, x):
	value = x.__dict__[name]
	if is_small_primitive_data(value):
		return horizontal_field(name, value)
	else:
		return vertical_field(name, value)

def present_python_object(x, fragment_view, inherited_state):
	attr_names = sorted(x.__dict__.keys())
	attrs = [_field(name, x)   for name in attr_names]
	attrs = Html(*attrs)

	t = Html.div(dropdown_expander(Html('Type'), type(x)))
	a = Html.div(dropdown_expander(Html('Attributes'), attrs))
	print repr(x)
	s = Html.div(dropdown_expander(Html('repr'), present_string(repr(x))))
	return Html('<div class="pythonobject">', Html(t, a, s), '</div>')



class LLInspectorPerspective (AbstractPerspective):
	def present_model(self, model, fragment_view, inherited_state):
		p = present_primitive_data(model)
		if p is not None:
			return p
		else:
			return present_python_object(model, fragment_view, inherited_state)

LLInspectorPerspective.instance = LLInspectorPerspective()

llinspect = LLInspectorPerspective.instance
