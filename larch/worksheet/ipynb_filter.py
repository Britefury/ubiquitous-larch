##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json

from larch.worksheet import worksheet


def load_json(ipynb):
	# Get the name
	notebook_name = ipynb['metadata']['name']
	nbformat, nbformat_minor = ipynb['nbformat'], ipynb['nbformat_minor']

	# Check the version
	if nbformat > 3  or  nbformat == 3  and  nbformat_minor > 0:
		raise ValueError, 'Unsupported notebook format {0}.{1}'.format(nbformat, nbformat_minor)

	# Iterate over the list of worksheets in the notebook
	ipynb_worksheets = ipynb['worksheets']

	larch_worksheets = []
	for ipynb_ws in ipynb_worksheets:
		# May contain data in the future
		ipynb_ws_metadata = ipynb_ws['metadata']

		larch_ws = worksheet.Worksheet([])
		larch_worksheets.append(larch_ws)

		cells = ipynb_ws['cells']

		for cell in cells:
			cell_type = cell['cell_type']
			cell_metadata = cell['metadata']
			if cell_type == 'code':
				if cell['language'] == 'python':
					cell_input = cell['input']
					source_code = ''.join(cell_input)
					block = worksheet.WorksheetBlockCode(larch_ws, code=source_code)
					larch_ws.append(block)
				else:
					raise ValueError, 'unknown language {0}'.format(cell['language'])
			elif cell_type == 'markdown':
				print 'Cannot currently convert markdown'
				source = cell['source']
				text = ''.join(source)
				block = worksheet.WorksheetBlockText(larch_ws, text=text)
				larch_ws.append(block)
			elif cell_type == 'raw':
				source = cell['source']
				text = ''.join(source)
				block = worksheet.WorksheetBlockText(larch_ws, text=text)
				larch_ws.append(block)
			elif cell_type == 'heading':
				level = cell['level']
				source = cell['source']
				text = ''.join(source)
				text = '<h{0}>{1}</h{0}>'.format(level, text)
				block = worksheet.WorksheetBlockText(larch_ws, text=text)
				larch_ws.append(block)
			else:
				raise ValueError, 'Unknown cell type {0}'.format(cell_type)

	return larch_worksheets, notebook_name



def loads(s):
	return load_json(json.loads(s))


def load(fp):
	return load_json(json.load(fp))