from __future__ import print_function, unicode_literals

import re

from collections import OrderedDict

# Valid characters for dictionary key
re_key = re.compile(r'[a-zA-Z0-9-_]+')
re_nums = re.compile(r'[0-9\.]+')
re_whitespace = re.compile(r'([ \t]+)')
re_leading_spaces = re.compile(r'^\s+', re.MULTILINE)
re_line = re.compile(r'.*')
re_sq = re.compile(r'\'([^\'\\]|\\.)*\'')
re_dq = re.compile(r'\"([^\"\\]|\\.)*\"')


class AttributeParser:
    """Parses comma-separated HamlPy attribute values"""

    def __init__(self, data, terminator):
        self.terminator = terminator
        self.s = data.lstrip()
        self.length = len(self.s)
        # Index of current character being read
        self.ptr = 1

    def consume_whitespace(self, include_newlines=False):
        """Moves the pointer to the next non-whitespace character"""
        whitespace = (' ', '\t', '\r', '\n') if include_newlines else (' ', '\t')

        while self.ptr < self.length and self.s[self.ptr] in whitespace:
            self.ptr += 1

        return self.ptr

    def consume_end_of_value(self):
        # End of value comma or end of string
        self.consume_whitespace()
        if self.s[self.ptr] != self.terminator:
            if self.s[self.ptr] == ',':
                self.ptr += 1
                self.consume_whitespace()
            else:
                raise Exception("Expected comma for end of value (after ...%s), but got '%s' instead" % (self.s[max(self.ptr - 10, 0):self.ptr], self.s[self.ptr]))

    def read_until_unescaped_character(self, closing):
        """
        Move the pointer until a *closing* character not preceded by a backslash is found.
        Returns the string found up to that point with any escaping backslashes removed
        """

        # Hardcoding some closing characters for efficiency
        # (tried a caching approach but it was too slow)
        if closing == "'":
            r = re_sq
        elif closing == '"':
            r = re_dq
        else:
            r = re.compile(r'%(c)s([^%(c)s\\]|\\.)*%(c)s' % dict(c=closing))

        m = r.match(self.s, pos=self.ptr)
        if m is None:
            raise Exception("Closing character not found")

        value = m.group(0)
        self.ptr += len(value)

        # Return all values in unicode
        return eval('u' + value)

    def parse_value(self):
        self.consume_whitespace()

        # Invalid initial value
        val = False

        if self.s[self.ptr] == self.terminator:
            return val

        # String
        if self.s[self.ptr] in ("'", '"'):
            quote = self.s[self.ptr]
            val = self.read_until_unescaped_character(quote)

        # Boolean Attributes
        elif self.s[self.ptr:self.ptr + 4].lower() == 'none':
            val = None
            self.ptr += 4

        # Integers and floats
        else:
            match = re_nums.match(self.s, pos=self.ptr)
            if match:
                val = match.group(0)
                self.ptr += len(val)

        if val is False:
            raise Exception("Failed to parse dictionary value beginning at: '%s'. Was expecting a string, None or a number." % self.s[self.ptr:])

        self.consume_end_of_value()

        return val


class AttributeDictParser(AttributeParser):
    """
    Parses a Haml element's attribute dictionary string and
    provides a Python dictionary of the element attributes
    """

    def __init__(self, s):
        AttributeParser.__init__(self, s, '}')
        self.dict = OrderedDict()

    def parse(self):
        while self.ptr < (self.length - 1):
            key = self.__parse_key()
            val = None
            is_bool_attr = False

            self.consume_whitespace()

            if self.s[self.ptr] == ':':  # python style : dict
                self.ptr += 1
            elif self.s[self.ptr:self.ptr + 2] == '=>':  # ruby style => dict
                self.ptr += 2
            elif self.s[self.ptr] in (',', '}'):  # valueless attribute
                self.ptr += 1
                is_bool_attr = True
            else:
                raise Exception("Expected colon ':'/comma ','/arrow '=>' for end of key (after ...%s), but got '%s' instead"
                                % (self.s[max(self.ptr - 10, 0):self.ptr], self.s[self.ptr]))

            if not is_bool_attr:
                self.consume_whitespace()

                # Multi-line HAML
                if self.s[self.ptr] == '\n':
                    self.ptr += 1
                    val = self.__parse_haml()
                    self.consume_whitespace()

                # Tuple/List parsing
                elif self.s[self.ptr] in ('(', '['):
                    tl_parser = AttributeTupleAndListParser(self.s[self.ptr:])
                    val = tl_parser.parse()
                    self.ptr += tl_parser.ptr
                    self.consume_end_of_value()

                else:
                    val = self.parse_value()

            self.dict[key] = val

        return self.dict

    def __parse_haml(self):
        def whitespace_length():
            r = re_whitespace.match(self.s, pos=self.ptr)
            return len(r.group(0))

        initial_indentation = whitespace_length()
        lines = []

        while whitespace_length() >= initial_indentation:
            line = re_line.match(self.s, pos=self.ptr).group(0)
            lines.append(line)
            self.ptr += len(line) + 1

        from .hamlpy import Compiler
        h = Compiler()
        html = h.process_lines(lines)
        return re.sub(re_leading_spaces, ' ', html).replace('\n', '').strip()

    def __parse_key(self):
        '''Parse key variable'''

        self.consume_whitespace(include_newlines=True)

        if self.s[self.ptr] == ':':
            self.ptr += 1

        # Consume opening quote
        quote = None
        if self.s[self.ptr] in ("'", '"'):
            quote = self.s[self.ptr]

        # Extract key
        if quote:
            key = self.read_until_unescaped_character(quote)
        else:
            key_match = re_key.match(self.s, pos=self.ptr)
            if key_match is None:
                raise Exception("Invalid key beginning at: %s" % self.s[self.ptr:])
            key = key_match.group(0)
            self.ptr += len(key)

        return key


class AttributeTupleAndListParser(AttributeParser):

    def __init__(self, s):
        if s[0] == '(':
            terminator = ')'
        elif s[0] == '[':
            terminator = ']'
        AttributeParser.__init__(self, s, terminator)

    def parse(self):
        lst = []

        val = True
        while val != False:
            val = self.parse_value()
            if val != False:
                lst.append(val)

        self.ptr += 1

        if self.terminator == ')':
            return tuple(lst)
        else:
            return lst
