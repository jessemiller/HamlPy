from __future__ import unicode_literals
"""
Core HamlPy filters.

The implementation of these should match https://github.com/haml/haml/blob/master/lib/haml/filters.rb as closely as
possible. Where we differ is that we don't compile Stylus, Coffeescript etc into CSS or Javascript - but place the
content into suitable <style> and <script> that can be transformed later by something like django-compressor.
"""

import sys
from io import StringIO

# Pygments and Markdown are optional dependencies which may or may not be available
try:
    import pygments
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import guess_lexer, PythonLexer
    from pygments.util import ClassNotFound

    _pygments_available = True
except ImportError:  # pragma: no cover
    _pygments_available = False

try:
    from markdown import markdown as markdown_lib

    _markdown_available = True
except ImportError:  # pragma: no cover
    _markdown_available = False

from .core import ParseException
from .utils import html_escape


# ----------------------------------------------------------------------------------
# Core filters
# ----------------------------------------------------------------------------------

def plain(text, options):
    return text


def preserve(text, options):
    text = text.rstrip()
    text = text.replace('\n', '&#x000A;')
    return text.replace('\r', '')


def escaped(text, options):
    return html_escape(text)


def cdata(text, options):
    text = '\n' + text.rstrip()
    text = text.replace("\n", "\n    ")
    return '<![CDATA[%s\n]]>' % text


def css(text, options):
    return style_filter(text, 'text/css', options)


def stylus(text, options):
    return style_filter(text, 'text/stylus', options)


def less(text, options):
    return style_filter(text, 'text/less', options)


def sass(text, options):
    return style_filter(text, 'text/sass', options)


def javascript(text, options):
    return script_filter(text, 'text/javascript', '//', options)


def coffee(text, options):
    return script_filter(text, 'text/coffeescript', '#', options)


def markdown(content, options):
    if not _markdown_available:
        raise ParseException("Markdown is not available")

    return markdown_lib(content)


def highlight(content, options):
    if not _pygments_available:
        raise ParseException("Pygments is not available")

    if content:
        # let Pygments try to guess syntax but default to Python
        try:
            lexer = guess_lexer(content)
        except ClassNotFound:
            lexer = PythonLexer()

        return pygments.highlight(content, lexer, HtmlFormatter())
    else:
        return ''


def python(content, options):
    if content:
        compiled_code = compile(content, "", "exec")
        output_buffer = StringIO()
        sys.stdout = output_buffer

        try:
            exec(compiled_code)
        except Exception as e:
            raise ParseException('Error whilst executing python filter node') from e
        finally:
            # restore the original stdout
            sys.stdout = sys.__stdout__

        return output_buffer.getvalue()
    else:
        return ''


# ----------------------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------------------

def style_filter(text, mime_type, options):
    indent = '    ' if options.cdata else '  '
    text = text.rstrip().replace('\n', '\n' + indent)
    type_attr = ' type=%(attr_wrapper)s%(mime_type)s%(attr_wrapper)s' % \
                {'attr_wrapper': options.attr_wrapper, 'mime_type': mime_type}
    before, after = ('  /*<![CDATA[*/\n', '  /*]]>*/\n') if options.cdata else ('', '')

    return '<style%s>\n%s%s%s\n%s</style>' % (type_attr, before, indent, text, after)


def script_filter(text, mime_type, comment, options):
    indent = '    ' if options.cdata else '  '
    text = text.rstrip().replace('\n', '\n' + indent)
    type_attr = ' type=%(attr_wrapper)s%(mime_type)s%(attr_wrapper)s' % \
                {'attr_wrapper': options.attr_wrapper, 'mime_type': mime_type}
    before, after = ('  %s<![CDATA[\n' % comment, '  %s]]>\n' % comment) if options.cdata else ('', '')

    return '<script%s>\n%s%s%s\n%s</script>' % (type_attr, before, indent, text, after)


# ----------------------------------------------------------------------------------
# Filter registration
# ----------------------------------------------------------------------------------

FILTERS = {
    'plain': plain,
    'preserve': preserve,
    'escaped': escaped,
    'cdata': cdata,
    'css': css,
    'stylus': stylus,
    'less': less,
    'sass': sass,
    'javascript': javascript,
    'coffee': coffee,
    'coffeescript': coffee,
    'markdown': markdown,
    'highlight': highlight,
    'python': python
}


def register_filter(name, callback):
    FILTERS[name] = callback


def get_filter(name):
    if name not in FILTERS:
        raise ParseException("No such filter: " + name)

    return FILTERS.get(name)
