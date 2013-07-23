##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************


def dependency_message(deps):
	return {'msgtype': 'add_dependencies',
		'deps': deps}


def modify_document_message(changes):
	return {'msgtype' : 'modify_document',
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
