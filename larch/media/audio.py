##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import struct
from larch.pres.resource import ConstResource
from larch.pres.html import Html


def audio_capture_button(num_channels, format, audio_data_callback):
	def _submit(event):
		num_channels = int(event.data['num_channels'])
		sample_rate = int(event.data['sample_rate'])
		num_samples = int(event.data['num_samples'])
		data_file = event.data['data'].file
		audio_data_callback(data_file, sample_rate, num_samples, num_channels)


	#options = {'text': text}
	button = Html('<button></button>').js_function_call('larch.media.initAudioCaptureButton', num_channels, format)
	button = button.with_event_handler('form_submit', _submit)
	button = button.use_js('/static/larch/larch_media.js')
	return button


def wav_player_from_rsc(rsc, width=500, height=100):
	return Html('<audio controls width="{0}" height="{1}"><source src="'.format(width, height), rsc, '" type="audio/wav"/></audio>')

def wav_player_from_data(data, width=500, height=100):
	return wav_player_from_rsc(ConstResource(data, 'audio/wav'), width, height)



def raw16_to_wav(data, sample_rate, num_channels):
	b = 'RIFF'		# Chunk ID
	b += struct.pack('<I', 44+len(data))		# ChunkSize
	b += 'WAVE'			# Format
	# FMT sub-chunk
	b += 'fmt '
	b += struct.pack('<IHHIIHH', 16,		# Subchunk1Size - 16 bytes
			 					1,		# AudioFormat: 1 = PCM
			 					num_channels,		# NumChannels
			 					sample_rate,		# SampleRate
			 					sample_rate * num_channels * 2,		# ByteRate = SampleRate * NumChannels * BytesPerSample
			 					num_channels * 2,		# BlockAlign = NumChannels * BytesPerSample
			 					16,		# BitsPerSample
	)
	# Data sub-chunk
	b += 'data'		# Subchunk2ID
	b += struct.pack('<I', len(data))
	b += data
	return b
