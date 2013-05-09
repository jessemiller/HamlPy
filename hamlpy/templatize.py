"""
This module decorates the django templatize function to parse haml templates
before the translation utility extracts tags from it.
"""

try:
    from django.utils.translation import trans_real
    _django_available = True
except ImportError, e:
    _django_available = False

import hamlpy


def decorate_templatize(func):
	def templatize(src, origin=None):
		hamlParser = hamlpy.Compiler()
		html = hamlParser.process(src.decode('utf-8'))
		return func(html.encode('utf-8'), origin)

	return templatize

if _django_available:
    trans_real.templatize = decorate_templatize(trans_real.templatize)

