from __future__ import print_function, unicode_literals

import re

from collections import OrderedDict

from .generic import (
    consume_whitespace, read_symbol, read_until, read_number, read_quoted_string, STRING_LITERALS, ParseException
)

ATTRIBUTE_KEY_REGEX = re.compile(r'[a-zA-Z0-9-_]+')


def read_attribute(stream, assignment_symbols, entry_separator, terminator):
    """
    Parses a single dictionary entry
    """
    consume_whitespace(stream, include_newlines=True)

    if stream.text[stream.ptr] in STRING_LITERALS:
        key = read_quoted_string(stream)
    else:
        # attribute keys may be prefixed with : which we ignore
        if stream.text[stream.ptr] == ':':
            stream.ptr += 1

        key = read_until(stream, ('}', ')', '=', ':'), or_whitespace=True)

    if not ATTRIBUTE_KEY_REGEX.match(key):
        raise ParseException("Invalid attribute key: %s" % key, stream)

    consume_whitespace(stream)

    if stream.text[stream.ptr] in (entry_separator, terminator):
        value = None
    else:
        read_symbol(stream, assignment_symbols)

        consume_whitespace(stream)

        if stream.text[stream.ptr] in STRING_LITERALS:
            value = read_quoted_string(stream)
        elif stream.text[stream.ptr].isdigit():
            value = read_number(stream)
        else:
            read_symbol(stream, ('None', 'none'))
            value = None

    return key, value


def read_attributes(stream):
    data = OrderedDict()

    start, terminator = stream.text[0], stream.text[-1]

    assert start in ('{', '(') and terminator in ('}', ')')

    if start == '{':
        assignment_symbols = ('=>', ':')
        entry_separator = ','
    else:
        assignment_symbols = ('=',)
        entry_separator = None

    stream.ptr += 1

    while True:
        consume_whitespace(stream, include_newlines=True)

        if stream.text[stream.ptr] == terminator:
            break

        key, value = read_attribute(stream, assignment_symbols, entry_separator, terminator)

        data[key] = value

        consume_whitespace(stream, include_newlines=True)

        if entry_separator and stream.text[stream.ptr] != terminator:
            read_symbol(stream, (entry_separator,))

    return data
