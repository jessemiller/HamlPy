import jinja2.ext
import os

from hamlpy import HAML_EXTENSIONS
from hamlpy.compiler import Compiler
from hamlpy.parser.core import ParseException


class HamlPyExtension(jinja2.ext.Extension):

    def preprocess(self, source, name, filename=None):
        extension = os.path.splitext(name)[1][1:]

        if extension in HAML_EXTENSIONS:
            compiler = Compiler()
            try:
                return compiler.process(source)
            except ParseException as e:
                raise jinja2.TemplateSyntaxError(str(e), 1, name=name, filename=filename)
        else:
            return source
