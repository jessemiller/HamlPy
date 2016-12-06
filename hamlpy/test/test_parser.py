# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from hamlpy.parser.generic import Stream, ParseException, consume_whitespace
from hamlpy.parser.generic import read_quoted_string, read_line, read_number, read_symbol, read_word


class ParserTest(unittest.TestCase):

    def test_consume_whitespace(self):
        stream = Stream(' \t foo  \n  bar   ')

        self.assertEqual(consume_whitespace(stream), ' \t ')
        self.assertEqual(stream.text[stream.ptr:], 'foo  \n  bar   ')

        stream.ptr += 3  # skip over foo

        self.assertEqual(consume_whitespace(stream), '  ')
        self.assertEqual(stream.text[stream.ptr:], '\n  bar   ')

        self.assertEqual(consume_whitespace(stream, include_newlines=True), '\n  ')
        self.assertEqual(stream.text[stream.ptr:], 'bar   ')

        stream.ptr += 3  # skip over bar

        self.assertEqual(consume_whitespace(stream), '   ')
        self.assertEqual(stream.text[stream.ptr:], '')

    def test_quoted_string(self):
        stream = Stream("'hello'---")
        self.assertEqual(read_quoted_string(stream), "hello")
        self.assertEqual(stream.text[stream.ptr:], '---')

        stream = Stream('"this don\'t \\"x\\" hmm" not in string')
        self.assertEqual(read_quoted_string(stream), 'this don\'t \"x\" hmm')
        self.assertEqual(stream.text[stream.ptr:], ' not in string')

        self.assertRaises(ParseException, read_quoted_string, Stream('"no end quote...'))

    def test_read_line(self):
        stream = Stream('line1\n line2\n\nline4\n\n')
        self.assertEqual(read_line(stream), 'line1')
        self.assertEqual(read_line(stream), ' line2')
        self.assertEqual(read_line(stream), '')
        self.assertEqual(read_line(stream), 'line4')
        self.assertEqual(read_line(stream), '')
        self.assertEqual(read_line(stream), None)

        self.assertEqual(read_line(Stream('last line  ')), 'last line  ')

    def test_read_number(self):
        stream = Stream('123"')
        self.assertEqual(read_number(stream), '123')
        self.assertEqual(stream.text[stream.ptr:], '"')

        stream = Stream('123.4xx')
        self.assertEqual(read_number(stream), '123.4')
        self.assertEqual(stream.text[stream.ptr:], 'xx')

        stream = Stream('0.0001   ')
        self.assertEqual(read_number(stream), '0.0001')
        self.assertEqual(stream.text[stream.ptr:], '   ')

    def test_read_symbol(self):
        stream = Stream('=> bar')
        self.assertEqual(read_symbol(stream, ['=>', ':']), '=>')
        self.assertEqual(stream.text[stream.ptr:], ' bar')

        self.assertRaises(ParseException, read_symbol, Stream('foo'), ['=>'])

    def test_read_word(self):
        stream = Stream('foo_bar')
        self.assertEqual(read_word(stream), 'foo_bar')
        self.assertEqual(stream.text[stream.ptr:], '')

        stream = Stream('foo_bar ')
        self.assertEqual(read_word(stream), 'foo_bar')
        self.assertEqual(stream.text[stream.ptr:], ' ')

        stream = Stream('ng-repeat(')
        self.assertEqual(read_word(stream), 'ng')
        self.assertEqual(stream.text[stream.ptr:], '-repeat(')

        stream = Stream('ng-repeat(')
        self.assertEqual(read_word(stream, include_hypens=True), 'ng-repeat')
        self.assertEqual(stream.text[stream.ptr:], '(')

        stream = Stream('これはテストです...')
        self.assertEqual(read_word(stream), 'これはテストです')
        self.assertEqual(stream.text[stream.ptr:], '...')
