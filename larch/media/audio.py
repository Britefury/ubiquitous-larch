##-*************************
##-* This source code is (C)copyright Geoffrey French 2011-2013.
##-*************************
import struct
from larch.pres.resource import ConstResource
from larch.pres.html import Html


FORMAT_WAV = 'wav'
FORMAT_RAW8 = 'raw8'
FORMAT_RAW16 = 'raw16'
FORMAT_RAW32 = 'raw32'

_valid_formats = {FORMAT_WAV, FORMAT_RAW8, FORMAT_RAW16, FORMAT_RAW32}


def audio_capture_button(num_channels, format, audio_data_callback):
	"""
	Create an audio capture button

	:param num_channels: the number of channels; 1 = mono, 2 = stereo
	:param format: the data format; valid formats are provided by constants in the larch.media.audio module:
		FORMAT_WAV: WAV file format
		FORMAT_RAW8: raw data, 8-bit signed integer per sample per channel
		FORMAT_RAW16:  raw data, 16-bit signed integer per sample per channel,
		FORMAT_RAWF32: raw data, 32-bit float per sample per channel
	audio_data_callback - a callback function that is invoked when audio data is received from the browser, of the form function(data_file, sample_rate, num_samples, num_channels), where:
		data_file - an object that contains the audio data, has a read method, the same kind of object as used to form file uploads.
		sample_rate - the sample rate of the received audio data, in Hz
		num_samples - the number of samples received; to get length in seconds, divide this number by sample_rate
		num_channels - the number of channels in the received data
	"""
	def _submit(event):
		num_channels = int(event.data['num_channels'])
		sample_rate = int(event.data['sample_rate'])
		num_samples = int(event.data['num_samples'])
		data_file = event.data['data'].file
		audio_data_callback(data_file, sample_rate, num_samples, num_channels)

	if format not in _valid_formats:
		raise ValueError, 'Unknown audio format \'{0}\''.format(format)

	button = Html('<button></button>').js_function_call('larch.media.initAudioCaptureButton', num_channels, format)
	button = button.with_event_handler('form_submit', _submit)
	button = button.use_js('/static/larch/larch_media.js')
	return button



def wav_player_from_rsc(rsc, width=500, height=100):
	"""
	Create a WAV audio player, with the data provided by a resource

	:param rsc: a resource that provides WAV format data
	:param width: width
	:param height: height
	"""
	return Html('<audio controls width="{0}" height="{1}"><source src="'.format(width, height), rsc, '" type="audio/wav"/></audio>')


def wav_player_from_data(data, width=500, height=100):
	"""
	Create a WAV audio player, with data provided in binary form, as a string

	:param data: binary WAV format data
	:param width: width
	:param height: height
	"""
	return wav_player_from_rsc(ConstResource(data, 'audio/wav'), width, height)



def raw16_to_wav(data, sample_rate, num_channels):
	"""
	Convert 16-bit RAW audio to WAV format; normally used to take RAW data and prepare it for playback in the broser

	:param data: RAW binary audio data, 16-bit signed integer per sample per channel
	:param sample_rate: the sample rate in Hz
	:param num_channels: the number of channels; 1 = mono, 2 = stereo
	"""
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
