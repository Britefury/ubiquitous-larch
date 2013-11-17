##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json
from larch.apps.notebook import notebook

try:
	import markdown
except ImportError:
	markdown = None

from larch.pres.html import Html



def get_name_from_ipynb_json(ipynb):
	"""
	Gets the name of an IPython notebook in JSON form

	:param ipynb: IPython notebook in JSON form
	:return: name (string)
	"""
	return ipynb['metadata']['name']


def convert_ipynb_json(ipynb):
	"""
	Converts an IPython notebook in JSON form to a list of Larch notebook

	:param ipynb: IPython notebook in JSON form
	:return: (notebooks, notebook_name)  where notebooks is a list of notebooks and notebook_name is the name of the IPython notebook
	"""
	# Get the name
	notebook_name = ipynb['metadata']['name']
	nbformat, nbformat_minor = ipynb['nbformat'], ipynb['nbformat_minor']

	# Check the version
	if nbformat > 3  or  nbformat == 3  and  nbformat_minor > 0:
		raise ValueError, 'Unsupported notebook format {0}.{1}'.format(nbformat, nbformat_minor)

	# Iterate over the list of worksheets in the notebook
	ipynb_worksheets = ipynb['worksheets']

	larch_notebooks = []
	for ipynb_ws in ipynb_worksheets:
		# May contain data in the future
		ipynb_ws_metadata = ipynb_ws['metadata']

		larch_ws = notebook.Notebook([])
		larch_notebooks.append(larch_ws)

		cells = ipynb_ws['cells']

		for cell in cells:
			cell_type = cell['cell_type']
			cell_metadata = cell['metadata']
			if cell_type == 'code':
				if cell['language'] == 'python':
					cell_input = cell['input']
					source_code = ''.join(cell_input)
					block = notebook.NotebookBlockCode(larch_ws, code=source_code)
					larch_ws.append(block)
				else:
					raise ValueError, 'unknown language {0}'.format(cell['language'])
			elif cell_type == 'markdown':
				source = cell['source']
				text = ''.join(source)
				if markdown is not None:
					text = markdown.markdown(text)
				block = notebook.NotebookBlockText(larch_ws, text=text)
				larch_ws.append(block)
			elif cell_type == 'raw':
				source = cell['source']
				text = ''.join(source)
				block = notebook.NotebookBlockText(larch_ws, text=text)
				larch_ws.append(block)
			elif cell_type == 'heading':
				level = cell['level']
				source = cell['source']
				text = ''.join(source)
				text = '<h{0}>{1}</h{0}>'.format(level, text)
				block = notebook.NotebookBlockText(larch_ws, text=text)
				larch_ws.append(block)
			else:
				raise ValueError, 'Unknown cell type {0}'.format(cell_type)

	return larch_notebooks, notebook_name



def loads(s):
	"""
	Imports an IPython notebook from a string

	:param s: IPython notebook JSON serialised as a string
	:return: (notebooks, notebook_name)  where notebooks in a list of notebooks and notebook_name is the name of the notebook
	"""
	return convert_ipynb_json(json.loads(s))


def load(fp):
	"""
	Imports an IPython notebook from a file

	:param fp: a file object that reads as an IPython notebook
	:return: (notebooks, notebook_name)  where notebooks in a list of notebooks and notebook_name is the name of the notebook
	"""
	return convert_ipynb_json(json.load(fp))



def markdown_warning():
	if markdown is not None:
		return None
	else:
		return Html('<div class="warning_box">',
			    '<p><span class="warning_text">Warning:</span> the Python <a href="https://pypi.python.org/pypi/Markdown">Markdown</a> library is not installed.</p>'
			    '<p>Many Python installations will allow you to install it from the command-line by typing:</p>',
			    '<p><span class="code">pip install markdown</span></p>',
			    '<p>Otherwise, instructions can be obtained from the documentation linked from the Markdown project page.</p>',
			    '</div>'
		)