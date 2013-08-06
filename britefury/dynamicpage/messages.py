##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************


def dependency_message(deps):
	return {'msgtype': 'add_dependencies',
		'deps': deps}


def modify_page_message(changes):
	return {'msgtype' : 'modify_page',
		'changes' : changes}


def execute_js_message(js_code):
	return {'msgtype' : 'execute_js',
		'js_code' : js_code}


def resources_modified_message(resource_ids):
	return {'msgtype': 'resources_modified',
		'resource_ids': list(resource_ids)}


def resources_disposed_message(resource_ids):
	return {'msgtype': 'resources_disposed',
		'resource_ids': list(resource_ids)}


def invalid_page_message():
	return {'msgtype': 'invalid_page'}


def reload_page_message(location, get_params):
	return {'msgtype': 'reload_page',
		'location': location,
		'get_params': get_params}



def error_handling_event_message(err_html, event_name, event_seg_id, event_model_type_name, handler_seg_id, handler_model_type_name):
	return {'msgtype': 'error_handling_event',
		'err_html': err_html,
		'event_name': event_name,
		'event_seg_id': event_seg_id,
		'event_model_type_name': event_model_type_name,
		'handler_seg_id': handler_seg_id,
		'handler_model_type_name': handler_model_type_name}


def error_during_update_message(err_html):
	return {'msgtype': 'error_during_update',
		'err_html': err_html}


def html_structure_fixes_message(fixes_by_model):
	return {'msgtype': 'html_structure_fixes',
		'fixes_by_model': fixes_by_model}