from __future__ import unicode_literals

import sys
import textwrap

# Required on Python 2 to accept non-unicode output
try:
    from StringIO import StringIO
except ImportError:
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


from future.utils import raise_from

from .core import ParseException


def plain(content, indent, options):
    return textwrap.dedent(content)


def cdata(content, indent, options):
    return indent + '<![CDATA[\n' \
           + content + '\n' \
           + indent + ']]>'


def css(content, indent, options):
    return '<style type=%(attr_wrapper)stext/css%(attr_wrapper)s>\n' \
           '/*<![CDATA[*/\n' % {'attr_wrapper': options['attr_wrapper']} \
           + content + '\n' \
           + '/*]]>*/\n</style>'


def stylus(content, indent, options):
    return indent + '<style type=%(attr_wrapper)stext/stylus%(attr_wrapper)s>\n' \
                    '/*<![CDATA[*/\n' % {'attr_wrapper': options['attr_wrapper']} \
           + textwrap.dedent(content) + '\n' \
           + indent + '/*]]>*/\n</style>'


def javascript(content, indent, options):
    return '<script type=%(attr_wrapper)stext/javascript%(attr_wrapper)s>\n' \
           '// <![CDATA[\n' % {'attr_wrapper': options['attr_wrapper']} \
           + (content + '\n' if content else '') \
           + '// ]]>\n</script>'


def coffeescript(content, indent, options):
    return '<script type=%(attr_wrapper)stext/coffeescript%(attr_wrapper)s>\n' \
           '#<![CDATA[\n' % {'attr_wrapper': options['attr_wrapper']} \
           + (content + '\n' if content else '') \
           + '#]]>\n</script>'


def markdown(content, indent, options):
    if not _markdown_available:
        raise ParseException("Markdown is not available")

    return markdown_lib(textwrap.dedent(content))


def highlight(content, indent, options):
    if not _pygments_available:
        raise ParseException("Pygments is not available")

    if content:
        content = textwrap.dedent(content)

        # let Pygments try to guess syntax but default to Python
        try:
            lexer = guess_lexer(content)
        except ClassNotFound:
            lexer = PythonLexer()

        return pygments.highlight(content, lexer, HtmlFormatter())
    else:
        return ''


def python(content, indent, options):
    if content:
        content = textwrap.dedent(content)
        compiled_code = compile(content, "", "exec")
        output_buffer = StringIO()
        sys.stdout = output_buffer

        try:
            exec(compiled_code)
        except Exception as e:
            raise_from(ParseException('Error whilst executing python filter node'), e)
        finally:
            # restore the original stdout
            sys.stdout = sys.__stdout__

        return output_buffer.getvalue()
    else:
        return ''


FILTERS = {
    'plain': plain,
    'cdata': cdata,
    'css': css,
    'stylus': stylus,
    'javascript': javascript,
    'coffee': coffeescript,
    'coffeescript': coffeescript,
    'markdown': markdown,
    'highlight': highlight,
    'python': python
}


def get_filter(name):
    if name not in FILTERS:
        raise ParseException("No such filter: " + name)

    return FILTERS.get(name)
