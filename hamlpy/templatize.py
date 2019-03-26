"""
This module decorates the django templatize function to parse haml templates
before the translation utility extracts tags from it.

--Modified to ignore non-haml files.
"""

try:
    from django.utils import translation
    _django_available = True
except ImportError, e:
    _django_available = False

import hamlpy
import os


def decorate_templatize(func):
    def templatize(src, origin=None, **kwargs):
        #if the template has no origin file then do not attempt to parse it with haml
        if origin:
            #if the template has a source file, then only parse it if it is haml
            if os.path.splitext(origin)[1].lower() in ['.'+x.lower() for x in hamlpy.VALID_EXTENSIONS]:
                hamlParser = hamlpy.Compiler()
                src = hamlParser.process(src)
        return func(src, origin=origin, **kwargs)
    return templatize

if _django_available:
    translation.templatize = decorate_templatize(translation.templatize)
