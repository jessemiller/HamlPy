from __future__ import absolute_import, print_function, unicode_literals

"""
This module decorates the django templatize function to parse haml templates before the translation utility extracts
tags from it.
"""

import os

from django.utils.translation import trans_real

from hamlpy import HAML_EXTENSIONS
from hamlpy.compiler import Compiler


def decorate_templatize(func):
    def templatize(src, origin=None):
        # if the template has no origin then don't attempt to convert it because we don't know if it's Haml
        if origin:
            extension = os.path.splitext(origin.name)[1][1:].lower()

            if extension in HAML_EXTENSIONS:
                compiler = Compiler()
                src = compiler.process(src)

        return func(src, origin)
    return templatize


trans_real.templatize = decorate_templatize(trans_real.templatize)
