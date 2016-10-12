from __future__ import print_function, unicode_literals

"""
This module decorates the django templatize function to parse haml templates
before the translation utility extracts tags from it.

--Modified to ignore non-haml files.
"""

try:
    from django.utils.translation import trans_real
    _django_available = True
except ImportError as e:
    _django_available = False

import hamlpy
import os


def decorate_templatize(func):
    def templatize(src, origin=None):
        #if the template has no origin file then do not attempt to parse it with haml
        if origin:
            #if the template has a source file, then only parse it if it is haml
            if os.path.splitext(origin)[1].lower() in ['.'+x.lower() for x in hamlpy.VALID_EXTENSIONS]:
                hamlParser = hamlpy.Compiler()
                html = hamlParser.process(src.decode('utf-8'))
                src = html.encode('utf-8')
        return func(src, origin)
    return templatize

if _django_available:
    trans_real.templatize = decorate_templatize(trans_real.templatize)
