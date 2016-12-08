from __future__ import print_function, unicode_literals

import regex

from collections import OrderedDict

from .generic import ParseException, read_whitespace, read_symbol, read_number, read_quoted_string, read_word
from .generic import peek_indentation, read_line, STRING_LITERALS

LEADING_SPACES_REGEX = regex.compile(r'^\s+', regex.V1 | regex.MULTILINE)


def read_attribute_value(stream):
    """
    Reads an attribute's value which may be a string, a number or None
    """
    ch = stream.text[stream.ptr]

    if ch in STRING_LITERALS:
        return read_quoted_string(stream)
    elif ch.isdigit():
        return read_number(stream)
    elif stream.text[stream.ptr:stream.ptr+4].lower() == 'none':
        stream.ptr += 4
        return None
    else:
        raise ParseException("Unexpected \"%s\"." % ch, stream)


def read_attribute_value_list(stream):
    """
    Reads an attribute value which is a list of other values
    """
    open_literal = stream.text[stream.ptr]

    assert open_literal in ('(', '[')

    read_tuple = open_literal == '('
    close_literal = ')' if read_tuple else ']'

    data = []

    stream.ptr += 1  # consume opening symbol

    while True:
        read_whitespace(stream)

        if stream.text[stream.ptr] == close_literal:
            break

        data.append(read_attribute_value(stream))

        read_whitespace(stream)

        if stream.text[stream.ptr] != close_literal:
            read_symbol(stream, (',',))

    stream.ptr += 1  # consume closing symbol

    return tuple(data) if read_tuple else data


def read_attribute_value_haml(stream):
    """
    Reads an attribute value which is a block of indented Haml
    """
    indentation = peek_indentation(stream)
    haml_lines = []

    # read lines below with higher indentation as this filter's content
    while stream.ptr < stream.length:
        line_indentation = peek_indentation(stream)

        if line_indentation is not None and line_indentation < indentation:
            break

        line = read_line(stream)

        # don't preserve whitespace on empty lines
        if line.isspace():
            line = ''

        haml_lines.append(line)

    stream.ptr -= 1  # un-consume final newline which will act as separator between this and next entry

    from ..compiler import Compiler
    haml = '\n'.join(haml_lines)
    html = Compiler().process(haml)

    # un-format into single line
    return LEADING_SPACES_REGEX.sub(' ', html).replace('\n', '').strip()


def read_attribute(stream, assignment_symbols, entry_separator, terminator):
    """
    Reads a single dictionary entry, e.g. :foo => "bar" or foo="bar"
    """
    if stream.text[stream.ptr] in STRING_LITERALS:
        key = read_quoted_string(stream)
    else:
        # attribute keys may be prefixed with : which we ignore
        if stream.text[stream.ptr] == ':':
            stream.ptr += 1

        key = read_word(stream, include_hypens=True)

    if not key:
        raise ParseException("Empty attribute key.", stream)

    read_whitespace(stream)

    if stream.text[stream.ptr] in (entry_separator, terminator):
        value = None
    else:
        read_symbol(stream, assignment_symbols)

        read_whitespace(stream)

        if stream.text[stream.ptr] == '\n':
            stream.ptr += 1

            value = read_attribute_value_haml(stream)
        elif stream.text[stream.ptr] in ('(', '['):
            value = read_attribute_value_list(stream)
        else:
            value = read_attribute_value(stream)

    return key, value


def read_attribute_dict(stream):
    """
    Reads an attribute dictionary, e.g. {:foo => "bar", a => 3} or (foo="bar" a=3)
    """
    data = OrderedDict()

    opener = stream.text[stream.ptr]

    assert opener in ('{', '(')

    if opener == '(':
        html_style = True
        terminator = ')'
    else:
        html_style = False
        terminator = '}'

    stream.ptr += 1

    def record_value(key, value):
        if key in data:
            raise ParseException("Duplicate attribute: \"%s\"." % key, stream)
        data[key] = value

    while True:
        read_whitespace(stream, include_newlines=True)

        if stream.ptr >= stream.length:
            raise ParseException("Unterminated attribute dictionary", stream)

        if stream.text[stream.ptr] == terminator:
            stream.ptr += 1
            break

        # (foo = "bar" a=3)
        if html_style:
            record_value(*read_attribute(stream, ('=',), None, terminator))

            read_whitespace(stream)

            if stream.text[stream.ptr] == ',':
                raise ParseException("Unexpected \",\".", stream)

        # {:foo => "bar", a=>3}
        else:
            record_value(*read_attribute(stream, ('=>', ':'), ',', terminator))

            read_whitespace(stream)

            if stream.text[stream.ptr] not in (terminator, '\n'):
                read_symbol(stream, (',',))

    return data
