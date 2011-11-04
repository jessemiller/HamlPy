"""
This module decorates the django templatize function to parse haml templates
before the translation utility extracts tags from it.
"""

from django.utils.translation import trans_real
import hamlpy


def decorate_templatize(func):
	def templatize(src, origin=None):
		hamlParser = hamlpy.Compiler()
		html = hamlParser.process(src)
		return func(html, origin)
	
	return templatize

trans_real.templatize = decorate_templatize(trans_real.templatize)

