from __future__ import print_function, unicode_literals

import re

from collections import OrderedDict

STRING_LITERALS = ('"', "'")
WHITESPACE_CHARS = (' ', '\t')
WHITESPACE_AND_NEWLINE_CHARS = (' ', '\t', '\r', '\n')

# Valid characters for dictionary key
re_key = re.compile(r'[a-zA-Z0-9-_]+')
re_nums = re.compile(r'[0-9\.]+')


class ParseException(Exception):
    def __init__(self, message, parser=None):
        self.message = message
        self.context = parser.text[parser.ptr:10] if parser else None

    def __str__(self):
        return "%s at %s" % (self.message, self.context) if self.context else self.message


class BaseParser(object):
    """
    Generic text parsing class
    """
    def __init__(self):
        self.text = None
        self.length = None
        self.ptr = None

    def set_input(self, text):
        self.text = text.strip()
        self.length = len(self.text)
        self.ptr = 0

    def consume_whitespace(self, include_newlines=False):
        """
        Moves the pointer to the next non-whitespace character
        """
        whitespace = WHITESPACE_AND_NEWLINE_CHARS if include_newlines else WHITESPACE_CHARS

        while self.ptr < self.length and self.text[self.ptr] in whitespace:
            self.ptr += 1

        return self.ptr

    def read_until(self, terminators, or_whitespace=False):
        start = self.ptr

        while True:
            if self.ptr >= self.length:
                raise ParseException("Expected %s but reached end of input" % ", ".join(terminators), self)

            if self.text[self.ptr] in terminators or (or_whitespace and self.text[self.ptr] in WHITESPACE_CHARS):
                break

            self.ptr += 1

        return self.text[start:self.ptr]

    def read_quoted_string(self):
        terminator = self.text[self.ptr]

        assert terminator in STRING_LITERALS

        self.ptr += 1  # consume opening quote
        start = self.ptr

        while True:
            if self.ptr >= self.length:
                raise ParseException("Unterminated string. Expected %s but reached end of input" % terminator, self)

            if self.text[self.ptr] == terminator and self.text[self.ptr - 1] != '\\':
                break

            self.ptr += 1

        self.ptr += 1  # consume closing quote

        return self.text[start:self.ptr-1]

    def read_number(self):
        start = self.ptr

        while True:
            if not self.text[self.ptr].isdigit() and self.text[self.ptr] != '.':
                break

            self.ptr += 1

        return self.text[start:self.ptr]

    def read_symbol(self, symbols):
        for symbol in symbols:
            if self.text[self.ptr:self.ptr+len(symbol)] == symbol:
                self.ptr += len(symbol)
                return symbol

        raise ParseException("Expected one of %s" % ', '.join(symbols), self)


class AttributesParser(BaseParser):
    """
    Parses an attribute dictionary which may be Ruby style, e.g. {foo => 1, bar => 2} or HTML style, e.g. (foo=1 bar=2)
    """
    def parse(self, text):
        self.set_input(text)

        data = OrderedDict()

        start, terminator = self.text[0], self.text[-1]

        assert start in ('{', '(') and terminator in ('}', ')')

        if start == '{':
            assignment_symbols = ('=>', ':')
            entry_separator = ','
        else:
            assignment_symbols = ('=',)
            entry_separator = None

        self.ptr += 1

        while True:
            self.consume_whitespace(include_newlines=True)

            if self.text[self.ptr] == terminator:
                break

            key, value = self._parse_entry(assignment_symbols, entry_separator, terminator)

            data[key] = value

            self.consume_whitespace(include_newlines=True)

            if entry_separator and self.text[self.ptr] != terminator:
                self.read_symbol((entry_separator,))

        return data

    def _parse_entry(self, assignment_symbols, entry_separator, terminator):
        """
        Parses a single dictionary entry
        """
        self.consume_whitespace(include_newlines=True)

        if self.text[self.ptr] in STRING_LITERALS:
            key = self.read_quoted_string()
        else:
            # attribute keys may be prefixed with : which we ignore
            if self.text[self.ptr] == ':':
                self.ptr += 1

            key = self.read_until(('}', ')', '=', ':'), or_whitespace=True)

        if not re_key.match(key):
            raise ParseException("Invalid attribute key: %s" % key, self)

        self.consume_whitespace()

        if self.text[self.ptr] in (entry_separator, terminator):
            value = None
        else:
            self.read_symbol(assignment_symbols)

            self.consume_whitespace()

            if self.text[self.ptr] in STRING_LITERALS:
                value = self.read_quoted_string()
            elif self.text[self.ptr].isdigit():
                value = self.read_number()
            else:
                self.read_symbol(('None', 'none'))
                value = None

        return key, value
