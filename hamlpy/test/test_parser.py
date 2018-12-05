import unittest

from hamlpy.parser.core import Stream, ParseException, read_whitespace, peek_indentation
from hamlpy.parser.core import read_quoted_string, read_line, read_number, read_symbol, read_word
from hamlpy.parser.utils import html_escape


class ParserTest(unittest.TestCase):

    def test_read_whitespace(self):
        stream = Stream(' \t foo  \n  bar   ')

        assert read_whitespace(stream) == ' \t '
        assert stream.text[stream.ptr:] == 'foo  \n  bar   '

        stream.ptr += 3  # skip over foo

        assert read_whitespace(stream) == '  '
        assert stream.text[stream.ptr:] == '\n  bar   '

        assert read_whitespace(stream, include_newlines=True) == '\n  '
        assert stream.text[stream.ptr:] == 'bar   '

        stream.ptr += 3  # skip over bar

        assert read_whitespace(stream) == '   '
        assert stream.text[stream.ptr:] == ''

    def test_peek_indentation(self):
        assert peek_indentation(Stream('content')) == 0
        assert peek_indentation(Stream('  content')) == 2
        assert peek_indentation(Stream('\n')) is None
        assert peek_indentation(Stream('    \n')) is None

    def test_quoted_string(self):
        stream = Stream("'hello'---")
        assert read_quoted_string(stream) == "hello"
        assert stream.text[stream.ptr:] == '---'

        stream = Stream('"this don\'t \\"x\\" hmm" not in string')
        assert read_quoted_string(stream) == 'this don\'t \"x\" hmm'
        assert stream.text[stream.ptr:] == ' not in string'

        self.assertRaises(ParseException, read_quoted_string, Stream('"no end quote...'))

    def test_read_line(self):
        stream = Stream('line1\n line2\n\nline4\n\n')
        assert read_line(stream) == 'line1'
        assert read_line(stream) == ' line2'
        assert read_line(stream) == ''
        assert read_line(stream) == 'line4'
        assert read_line(stream) == ''
        assert read_line(stream) is None

        assert read_line(Stream('last line  ')) == 'last line  '

    def test_read_number(self):
        stream = Stream('123"')
        assert read_number(stream) == '123'
        assert stream.text[stream.ptr:] == '"'

        stream = Stream('123.4xx')
        assert read_number(stream) == '123.4'
        assert stream.text[stream.ptr:] == 'xx'

        stream = Stream('0.0001   ')
        assert read_number(stream) == '0.0001'
        assert stream.text[stream.ptr:] == '   '

    def test_read_symbol(self):
        stream = Stream('=> bar')
        assert read_symbol(stream, ['=>', ':']) == '=>'
        assert stream.text[stream.ptr:] == ' bar'

        self.assertRaises(ParseException, read_symbol, Stream('foo'), ['=>'])

    def test_read_word(self):
        stream = Stream('foo_bar')
        assert read_word(stream) == 'foo_bar'
        assert stream.text[stream.ptr:] == ''

        stream = Stream('foo_bar ')
        assert read_word(stream) == 'foo_bar'
        assert stream.text[stream.ptr:] == ' '

        stream = Stream('ng-repeat(')
        assert read_word(stream) == 'ng'
        assert stream.text[stream.ptr:] == '-repeat('

        stream = Stream('ng-repeat(')
        assert read_word(stream, ('-',)) == 'ng-repeat'
        assert stream.text[stream.ptr:] == '('

        stream = Stream('これはテストです...')
        assert read_word(stream) == 'これはテストです'
        assert stream.text[stream.ptr:] == '...'


class UtilsTest(unittest.TestCase):

    def test_html_escape(self):
        assert html_escape('') == ''
        assert html_escape('&<>"\'') == '&amp;&lt;&gt;&quot;&#39;'
        assert html_escape('{% trans "hello" %}') == '{% trans "hello" %}'
        assert html_escape('{{ foo|default:"hello" }}') == '{{ foo|default:"hello" }}'
        assert html_escape('{% }} & %}') == '{% }} & %}'

        result = html_escape('<>{% trans "hello" %}<>{{ foo|default:"hello" }}<>')
        assert result == '&lt;&gt;{% trans "hello" %}&lt;&gt;{{ foo|default:"hello" }}&lt;&gt;'
