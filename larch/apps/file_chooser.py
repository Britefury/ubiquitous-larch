import urllib2

from larch.pres.html import Html
from larch.controls import button, form, text_entry
from larch.live import LiveValue



def upload_file_chooser(on_choose, on_cancel):
	"""
	Create a file chooser dialog

	:param on_choose: a callback that is invoked when the use chooses a file. It is of the form function(fp) where fp is a file like object

	"""
	def _on_upload(event):
		f = event.data.get('file')
		if f is not None:
			on_choose(f.file)
		else:
			on_cancel()


	def _on_cancel(event):
		on_cancel()

	upload_form_contents = Html('<div><input type="file" name="file" size="50"/></div>',
				    '<table>',
				    '<tr><td>', button.button('Cancel', _on_cancel), '</td><td>', form.submit_button('Upload'), '</td></tr>',
				    '</table>')
	upload_form = form.form(upload_form_contents, _on_upload)

	return upload_form



def fetch_from_web_file_chooser(on_downloaded, on_cancel, user_agent=None):
	if user_agent is None:
		user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13'
	url_live = LiveValue()

	def on_fetch(event):
		url = url_live.static_value
		url_l = url.lower()
		if not url_l.startswith('http://')  and  not url_l.startswith('https://'):
			url = 'http://' + url
		request = urllib2.Request(url)
		request.add_header('User-Agent', user_agent)
		opener = urllib2.build_opener()
		fp = opener.open(request)

		on_downloaded(fp)

	def _on_cancel(event):
		on_cancel()

	return Html('<div><span class="gui_label">Web address (Github/Bitbucket RAW, etc):</span></div>',
			'<div><span>', text_entry.live_text_entry(url_live, width="40em"), '</span></div>',
			'<table>',
			'<tr><td>', button.button('Cancel', _on_cancel), '</td><td>', button.button('Fetch', on_fetch), '</td></tr>',
			'</table>',
			'</div>')



