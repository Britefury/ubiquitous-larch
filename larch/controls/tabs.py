##-*************************
##-* This program is free software; you can use it, redistribute it and/or
##-* modify it under the terms of the GNU Affero General Public License
##-* version 3 as published by the Free Software Foundation. The full text of
##-* the GNU Affero General Public License version 3 can be found in the file
##-* named 'LICENSE.txt' that accompanies this program. This source code is
##-* (C)copyright Geoffrey French 2011-2014.
##-*************************
from larch.pres import pres
from larch.pres.html import Html


class tabs (pres.CompositePres):
	__tab_counter = 0

	def __init__(self, tab_label_and_content_pairs):
		self.__tab_label_and_content_pairs = tab_label_and_content_pairs


	def pres(self, pres_ctx):
		contents = ['<div><ul>']
		for i, (tab, content) in enumerate(self.__tab_label_and_content_pairs):
			contents.extend(['<li><a href="#__larch_tabs_{0}_{1}">'.format(self.__tab_counter, i), tab, '</a></li>'])
		contents.append('</ul>')
		for i, (tab, content) in enumerate(self.__tab_label_and_content_pairs):
			contents.extend(['<div id="__larch_tabs_{0}_{1}">'.format(self.__tab_counter, i), content, '</div>'])
		contents.append('</div>')

		tabs.__tab_counter += 1

		t = Html(*contents)
		t = t.js_function_call('larch.controls.initTabs')
		t = t.use_js('/static/larch/larch_ui.js').use_css('/static/larch/larch_ui.css')
		return t