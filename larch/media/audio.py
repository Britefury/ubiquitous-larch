##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
from larch.pres.resource import ConstResource
from larch.pres.html import Html


def audio_capture_button(text, num_channels, format, audio_data_callback):
	def _submit(event):
		data_file = event.data['data'].file
		audio_data_callback(data_file)


	#options = {'text': text}
	options = {}
	button = Html('<button>{0}</button>'.format(text)).js_function_call('larch.media.initAudioCaptureButton', options, num_channels, format)
	button = button.with_event_handler('form_submit', _submit)
	button = button.use_js('/static/larch/larch_media.js')
	return button


def wav_from_rsc(rsc, width=500, height=100):
	return Html('<audio controls width="{0}" height="{1}"><source src="'.format(width, height), rsc, '" type="audio/wav"/></audio>')

def wav_from_data(data, width=500, height=100):
	return wav_from_rsc(ConstResource(data, 'audio/wav'), width, height)