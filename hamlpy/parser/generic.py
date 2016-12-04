from __future__ import unicode_literals

import ast

STRING_LITERALS = ('"', "'")
WHITESPACE_CHARS = (' ', '\t')
WHITESPACE_AND_NEWLINE_CHARS = (' ', '\t', '\r', '\n')


class ParseException(Exception):
    def __init__(self, message, stream):
        context = stream.text[max(stream.ptr-31, 0):stream.ptr+1]
        message = "%s @ \"%s\" <-" % (message, context)

        super(ParseException, self).__init__(message)


class Stream(object):
    def __init__(self, text):
        self.text = text
        self.length = len(self.text)
        self.ptr = 0


def consume_whitespace(stream, include_newlines=False):
    """
    Reads and discards whitespace characters
    """
    whitespace = WHITESPACE_AND_NEWLINE_CHARS if include_newlines else WHITESPACE_CHARS

    while stream.ptr < stream.length and stream.text[stream.ptr] in whitespace:
        stream.ptr += 1


def read_quoted_string(stream):
    """
    Reads a single or double quoted string, returning the value without the quotes
    """
    terminator = stream.text[stream.ptr]

    assert terminator in STRING_LITERALS

    start = stream.ptr
    stream.ptr += 1  # consume opening quote

    while True:
        if stream.ptr >= stream.length:
            raise ParseException("Unterminated string (expected %s)." % terminator, stream)

        if stream.text[stream.ptr] == terminator and stream.text[stream.ptr - 1] != '\\':
            break

        stream.ptr += 1

    stream.ptr += 1  # consume closing quote

    # evaluate as a Python unicode string (evaluates escape sequences)
    return ast.literal_eval('u' + stream.text[start:stream.ptr])


def read_number(stream):
    """
    Reads a decimal number, returning value as string
    """
    start = stream.ptr

    while True:
        if not stream.text[stream.ptr].isdigit() and stream.text[stream.ptr] != '.':
            break

        stream.ptr += 1

    return stream.text[start:stream.ptr]


def read_symbol(stream, symbols):
    """
    Reads one of the given symbols, returning its value
    """
    for symbol in symbols:
        if stream.text[stream.ptr:stream.ptr+len(symbol)] == symbol:
            stream.ptr += len(symbol)
            return symbol

    raise ParseException("Expected %s." % ' or '.join(['"%s"' % s for s in symbols]), stream)
