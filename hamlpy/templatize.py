from __future__ import absolute_import, print_function, unicode_literals

"""
This module decorates the django templatize function to parse haml templates
before the translation utility extracts tags from it.

--Modified to ignore non-haml files.
"""

import os

from django.utils.translation import trans_real

from hamlpy import hamlpy


def decorate_templatize(func):
    def templatize(src, origin=None):
        # if the template has no origin then don't attempt to convert it because we don't know if it's Haml
        if origin:
            extension = os.path.splitext(origin.name)[1][1:].lower()

            if extension in hamlpy.VALID_EXTENSIONS:
                compiler = hamlpy.Compiler()
                html = compiler.process(src.decode('utf-8'))
                src = html.encode('utf-8')

        return func(src, origin)
    return templatize


trans_real.templatize = decorate_templatize(trans_real.templatize)
