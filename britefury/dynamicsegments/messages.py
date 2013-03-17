##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************


def dependency_message(deps):
	return {'msgtype': 'add_dependencies', 'deps': deps}


def modify_document_message(changes):
	return {'msgtype' : 'modify_document', 'changes' : changes}


def execute_js_message(js_code):
	return {'msgtype' : 'execute_js', 'js_code' : js_code}


