"""
This module decorates the django templatize function to parse haml templates before the translation utility extracts
tags from it.
"""

import os

from django.utils import translation

from hamlpy import HAML_EXTENSIONS
from hamlpy.compiler import Compiler


def patch_templatize(func):
    def templatize(src, origin=None, charset='utf-8'):
        # if the template has no origin then don't attempt to convert it because we don't know if it's Haml
        if origin:
            extension = os.path.splitext(origin)[1][1:].lower()

            if extension in HAML_EXTENSIONS:
                compiler = Compiler()
                src = compiler.process(src)

        return func(src, origin=origin)
    return templatize


translation.templatize = patch_templatize(translation.templatize)
