import regex

from collections import OrderedDict

from .core import ParseException, read_whitespace, read_symbol, read_number, read_quoted_string, read_word
from .core import peek_indentation, read_line, STRING_LITERALS, WHITESPACE_CHARS
from .utils import html_escape

LEADING_SPACES_REGEX = regex.compile(r'^\s+', regex.V1 | regex.MULTILINE)

# non-word characters that we allow in attribute keys (in HTML style attribute dicts)
ATTRIBUTE_KEY_EXTRA_CHARS = {':', '-', '$', '?', '[', ']'}

ATTRIBUTE_VALUE_KEYWORDS = {'none': None, 'true': True, 'false': False}


def read_attribute_value(stream, compiler):
    """
    Reads an attribute's value which may be a string, a number or None
    """
    ch = stream.text[stream.ptr]

    if ch in STRING_LITERALS:
        value = read_quoted_string(stream)

        if compiler.options.escape_attrs:
            # TODO handle escape_attrs=once
            value = html_escape(value)

    elif ch.isdigit():
        value = read_number(stream)
    else:
        raw_value = read_word(stream)

        if raw_value.lower() in ATTRIBUTE_VALUE_KEYWORDS:
            value = ATTRIBUTE_VALUE_KEYWORDS[raw_value.lower()]
        else:
            value = '{{ %s }}' % raw_value

    return value


def read_attribute_value_list(stream, compiler):
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

        data.append(read_attribute_value(stream, compiler))

        read_whitespace(stream)

        if stream.text[stream.ptr] != close_literal:
            read_symbol(stream, (',',))

    stream.ptr += 1  # consume closing symbol

    return data


def read_attribute_value_haml(stream, compiler):
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

    haml = '\n'.join(haml_lines)
    html = compiler.process(haml)

    # un-format into single line
    return LEADING_SPACES_REGEX.sub(' ', html).replace('\n', '').strip()


def read_ruby_attribute(stream, compiler):
    """
    Reads a Ruby style attribute, e.g. :foo => "bar" or foo: "bar"
    """
    old_style = stream.text[stream.ptr] == ':'

    if old_style:
        stream.ptr += 1

        key = read_word(stream, include_chars=('-',))
    else:
        # new style Ruby / Python style allows attribute to be quoted string
        if stream.text[stream.ptr] in STRING_LITERALS:
            key = read_quoted_string(stream)

            if not key:
                raise ParseException("Attribute name can't be an empty string.", stream)
        else:
            key = read_word(stream, include_chars=('-',))

    read_whitespace(stream)

    if stream.text[stream.ptr] in ('=', ':'):
        if old_style:
            read_symbol(stream, ('=>',))
        else:
            read_symbol(stream, (':',))

        read_whitespace(stream, include_newlines=False)

        stream.expect_input()

        if stream.text[stream.ptr] == '\n':
            stream.ptr += 1

            value = read_attribute_value_haml(stream, compiler)
        elif stream.text[stream.ptr] in ('(', '['):
            value = read_attribute_value_list(stream, compiler)
        else:
            value = read_attribute_value(stream, compiler)
    else:
        value = True

    return key, value


def read_html_attribute(stream, compiler):
    """
    Reads an HTML style attribute, e.g. foo="bar"
    """
    key = read_word(stream, include_chars=ATTRIBUTE_KEY_EXTRA_CHARS)

    # can't have attributes without whitespace separating them
    ch = stream.text[stream.ptr]
    if ch not in WHITESPACE_CHARS and ch not in ('=', ')'):
        stream.raise_unexpected()

    read_whitespace(stream)

    if stream.text[stream.ptr] == '=':
        read_symbol(stream, '=')

        read_whitespace(stream, include_newlines=False)

        stream.expect_input()

        if stream.text[stream.ptr] == '\n':
            stream.ptr += 1

            value = read_attribute_value_haml(stream, compiler)
        elif stream.text[stream.ptr] == '[':
            value = read_attribute_value_list(stream, compiler)
        else:
            value = read_attribute_value(stream, compiler)
    else:
        value = True

    return key, value


def read_attribute_dict(stream, compiler):
    """
    Reads an attribute dictionary which may use one of 3 syntaxes:
     1. {:foo => "bar", :a => 3}  (old Ruby)
     2. {foo: "bar", a: 3}  (new Ruby / Python)
     3. (foo="bar" a=3)  (HTML)
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
            record_value(*read_html_attribute(stream, compiler))

            read_whitespace(stream)

            if stream.text[stream.ptr] == ',':
                raise ParseException("Unexpected \",\".", stream)

        # {:foo => "bar", :a=>3} or {foo: "bar", a: 3}
        else:
            record_value(*read_ruby_attribute(stream, compiler))

            read_whitespace(stream)

            if stream.text[stream.ptr] not in (terminator, '\n'):
                read_symbol(stream, (',',))

    return data
