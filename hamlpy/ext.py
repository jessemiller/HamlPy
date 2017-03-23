# coding=utf-8
try:
    import jinja2.ext
    _jinja2_available = True
except ImportError, e:
    _jinja2_available = False

import hamlpy
import os

HAML_FILE_NAME_EXTENSIONS = ['haml', 'hamlpy']


def clean_extension(file_ext):
    if not isinstance(file_ext, basestring):
        raise Exception('Wrong file extension format: %r' % file_ext)
    if len(file_ext) > 1 and file_ext.startswith('.'):
        file_ext = file_ext[1:]
    return file_ext.lower().strip()


def get_file_extension(file_path):
    file_ext = os.path.splitext(file_path)[1]
    return clean_extension(file_ext)


def has_any_extension(file_path, extensions):
    file_ext = get_file_extension(file_path)
    return file_ext and extensions and file_ext in [clean_extension(e) for e in extensions]

if _jinja2_available:
    class HamlPyExtension(jinja2.ext.Extension):

        def preprocess(self, source, name, filename=None):
            if name and has_any_extension(name, HAML_FILE_NAME_EXTENSIONS):
                compiler = hamlpy.Compiler()
                try:
                    return compiler.process(source)
                except Exception as e:
                    raise jinja2.TemplateSyntaxError(e, 1, name=name, filename=filename)
            else:
                return source
