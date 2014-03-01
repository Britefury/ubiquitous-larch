##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************

import os
import glob


PRINT_ONLY = True


#
# Licenses
#

_old_css_licenses = [
	"""/*************************
-* This source code is (C)copyright Geoffrey French 2011-2013.
-*************************/""",
]

_new_css_license = """/*************************
-* This program is free software; you can use it, redistribute it and/or
-* modify it under the terms of the GNU Affero General Public License
-* version 3 as published by the Free Software Foundation. The full text of
-* the GNU Affero General Public License version 3 can be found in the file
-* named 'LICENSE.txt' that accompanies this program. This source code is
-* (C)copyright Geoffrey French 2011-2014.
-*************************/"""


_old_js_licenses = [
	"""//-*************************
//-* This source code is (C)copyright Geoffrey French 2011-2013.
//-*************************""",
]

_new_js_license = """//-*************************
//-* This program is free software; you can use it, redistribute it and/or
//-* modify it under the terms of the GNU Affero General Public License
//-* version 3 as published by the Free Software Foundation. The full text of
//-* the GNU Affero General Public License version 3 can be found in the file
//-* named 'LICENSE.txt' that accompanies this program. This source code is
//-* (C)copyright Geoffrey French 2011-2014.
//-*************************"""


_old_py_licenses = [
	"""##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************""",
]

_new_py_license ="""##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
##-*************************"""


_old_css_licenses_as_lines = [license.split('\n')   for license in _old_css_licenses]
_old_js_licenses_as_lines = [license.split('\n')   for license in _old_js_licenses]
_old_py_licenses_as_lines = [license.split('\n')   for license in _old_py_licenses]

_new_css_license_writeable_lines = [l + '\n'   for l in _new_css_license.split('\n')]
_new_js_license_writeable_lines = [l + '\n'   for l in _new_js_license.split('\n')]
_new_py_license_writeable_lines = [l + '\n'   for l in _new_py_license.split('\n')]


#
# License replacement function
#

def _replace_license(path, old_licenses_as_lines, new_license_writeable_lines):
	license_length = None

	with open(path, 'r') as f:
		# Read the contents of the file
		f_lines = f.readlines()

		# Find the license
		for old_license_as_lines in old_licenses_as_lines:
			match = True
			for l, f in zip(old_license_as_lines, f_lines):
				if l.strip() != f.strip():
					match = False
			if match:
				license_length = len(old_license_as_lines)
				break

	if license_length is not None:
		new_lines = new_license_writeable_lines + f_lines[license_length:]
		if not PRINT_ONLY:
			with open(path, 'w') as f:
				f.writelines(new_lines)
		print 'Replaced {0}'.format(path)
	else:
		print '**IGNORED** {0}'.format(path)






#
# Handlers
#

def _handle_py(path):
	_replace_license(path, _old_py_licenses_as_lines, _new_py_license_writeable_lines)

def _handle_css(path):
	_replace_license(path, _old_css_licenses_as_lines, _new_css_license_writeable_lines)

def _handle_js(path):
	_replace_license(path, _old_js_licenses_as_lines, _new_js_license_writeable_lines)

_ext_handlers = {
	'.py': _handle_py,
	'.css': _handle_css,
	'.js': _handle_js,
}




#
# Process a file
#

def process_file(path):
	_, ext = os.path.splitext(path)
	ext = ext.lower()
	handler = _ext_handlers.get(ext.lower())
	if handler is not None:
		handler(path)




#
# Root directory listing
#

root_directories = [
	'larch',
	'static/larch'
]

#
# Walk the project files
#

for root in root_directories:
	def visit(arg, path, files):
		for f in files:
			p = os.path.join(path, f)
			process_file(p)

	os.path.walk(root, visit, None)


for f in glob.glob('*.py'):
	if os.path.isfile(f):
		if f.lower() != 'bottle.py':
			process_file(f)