##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import json

from britefury.pres.key_event import Key


class Command (object):
	def __init__(self, key_sequence, description, on_invoke):
		"""Constructructor

		key_sequence - the sequence of key presses used to invoke the command
		description - command description
		on_invoke - function() that invokes the command
		"""
		self.key_sequence = key_sequence
		self.description = description
		self.on_invoke = on_invoke
		self._command_id = 'cmd{0}'.format(id(self))

	def invoke(self):
		self.on_invoke()


	def js_expr(self):
		key_jsons = [k.__to_json__()   for k in self.key_sequence]
		key_json_strs = [json.dumps(k)   for k in key_jsons]
		return 'larch.registerCommand([{0}], "{1}")'.format(', '.join(key_json_strs), self._command_id)


class CommandSet (object):
	def __init__(self, commands=None):
		if commands is None:
			commands = []
		self.commands = commands
		self._id_to_command = {}
		for command in commands:
			self._id_to_command[command._command_id] = command



	def invoke_by_command_id(self, command_id):
		self._id_to_command[command_id].invoke()


	def __iter__(self):
		return iter(self.commands)


	def attach_to_document(self, dynamic_document):
		for command in self.commands:
			dynamic_document.queue_js_to_execute(command.js_expr())
		dynamic_document.add_document_event_handler('command', self.invoke_by_command_id)



