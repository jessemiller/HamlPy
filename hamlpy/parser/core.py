import ast

STRING_LITERALS = ('"', "'")
WHITESPACE_CHARS = (' ', '\t')
WHITESPACE_AND_NEWLINE_CHARS = (' ', '\t', '\r', '\n')


class ParseException(Exception):
    def __init__(self, message, stream=None):
        if stream:
            context = stream.text[max(stream.ptr-31, 0):stream.ptr+1]
            message = "%s @ \"%s\" <-" % (message, context)

        super(ParseException, self).__init__(message)


class Stream(object):
    def __init__(self, text):
        self.text = text
        self.length = len(self.text)
        self.ptr = 0

    def expect_input(self):
        """
        We expect more input, raise exception if there isn't any
        """
        if self.ptr >= self.length:
            raise ParseException("Unexpected end of input.", self)

    def raise_unexpected(self):
        """
        Raises exception that current character is unexpected
        """
        raise ParseException("Unexpected \"%s\"." % self.text[self.ptr], self)

    def __repr__(self):  # pragma: no cover
        return '"%s" >> "%s"' \
               % (self.text[:self.ptr].replace('\n', '\\n'), self.text[self.ptr:].replace('\n', '\\n'))


class TreeNode(object):
    """
    Generic parent/child tree class
    """
    def __init__(self):
        self.parent = None
        self.children = []

    def left_sibling(self):
        siblings = self.parent.children
        index = siblings.index(self)
        return siblings[index - 1] if index > 0 else None

    def right_sibling(self):
        siblings = self.parent.children
        index = siblings.index(self)
        return siblings[index + 1] if index < len(siblings) - 1 else None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


def read_whitespace(stream, include_newlines=False):
    """
    Reads whitespace characters, returning the whitespace characters
    """
    whitespace = WHITESPACE_AND_NEWLINE_CHARS if include_newlines else WHITESPACE_CHARS

    start = stream.ptr

    while stream.ptr < stream.length and stream.text[stream.ptr] in whitespace:
        stream.ptr += 1

    return stream.text[start:stream.ptr]


def peek_indentation(stream):
    """
    Counts but doesn't actually read indentation level on new line, returning the count or None if line is blank
    """
    indentation = 0
    while True:
        ch = stream.text[stream.ptr + indentation]
        if ch == '\n':
            return None

        if not ch.isspace():
            return indentation

        indentation += 1


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

    # evaluate as a Python string (evaluates escape sequences)
    return ast.literal_eval(stream.text[start:stream.ptr])


def read_line(stream):
    """
    Reads a line
    """
    start = stream.ptr

    if stream.ptr >= stream.length:
        return None

    while stream.ptr < stream.length and stream.text[stream.ptr] != '\n':
        stream.ptr += 1

    line = stream.text[start:stream.ptr]

    if stream.ptr < stream.length and stream.text[stream.ptr] == '\n':
        stream.ptr += 1

    return line


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


def read_word(stream, include_chars=()):
    """
    Reads a sequence of word characters
    """
    stream.expect_input()

    start = stream.ptr

    while stream.ptr < stream.length:
        ch = stream.text[stream.ptr]
        if not (ch.isalnum() or ch == '_' or ch in include_chars):
            break
        stream.ptr += 1

    # if we immediately hit a non-word character, raise it as unexpected
    if start == stream.ptr:
        stream.raise_unexpected()

    return stream.text[start:stream.ptr]
