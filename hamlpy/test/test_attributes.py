from __future__ import unicode_literals

import unittest

from collections import OrderedDict

from hamlpy.parser.attributes import read_attribute_dict
from hamlpy.parser.generic import Stream, ParseException


class AttributeDictParserTest(unittest.TestCase):

    @staticmethod
    def _parse(text):
        return read_attribute_dict(Stream(text))

    def test_read_attribute_dict(self):
        # empty dict
        stream = Stream("{}><")
        self.assertEqual(dict(read_attribute_dict(stream)), {})
        self.assertEqual(stream.text[stream.ptr:], '><')

        # string values
        self.assertEqual(dict(self._parse("{'class': 'test'} =Test")), {'class': 'test'})
        self.assertEqual(dict(self._parse("{'class': 'test', 'id': 'something'}")),
                         {'class': 'test', 'id': 'something'})

        # integer values
        self.assertEqual(dict(self._parse("{'data-number': 0}")), {'data-number': '0'})
        self.assertEqual(dict(self._parse("{'data-number': 12345}")), {'data-number': '12345'})

        # float values
        self.assertEqual(dict(self._parse("{'data-number': 123.456}")), {'data-number': '123.456'})
        self.assertEqual(dict(self._parse("{'data-number': 0.001}")), {'data-number': '0.001'})

        # None value
        self.assertEqual(dict(self._parse("{'controls': None}")), {'controls': None})

        # implicit boolean value
        self.assertEqual(dict(self._parse("{'data-number'}")), {'data-number': None})

        # attribute name has colon
        self.assertEqual(dict(self._parse("{'xml:lang': 'en'}")), {'xml:lang': 'en'})

        # attribute value has colon or commas
        self.assertEqual(dict(self._parse("{'lang': 'en:g'}")), {'lang': 'en:g'})
        self.assertEqual(dict(self._parse(
            '{name:"viewport", content:"width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1"}'
        )), {'name': 'viewport', 'content': 'width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1'})

        # double quotes
        self.assertEqual(dict(self._parse('{"class": "test", "id": "something"}')),
                         {'class': 'test', 'id': 'something'})

        # no quotes for key
        self.assertEqual(dict(self._parse("{class: 'test', id: 'something'}")),
                         {'class': 'test', 'id': 'something'})

        # whitespace is ignored
        self.assertEqual(dict(self._parse("{   class  \t :        'test',     data-number:    123  }")),
                         {'class': 'test', 'data-number': '123'})

        # trailing commas are fine
        self.assertEqual(dict(self._parse("{class: 'test', data-number: 123,}")),
                         {'class': 'test', 'data-number': '123'})

        # attributes split onto multiple lines
        self.assertEqual(dict(self._parse("{class: 'test',\n     data-number: 123}")),
                         {'class': 'test', 'data-number': '123'})

        # Ruby style arrows
        self.assertEqual(dict(self._parse("{'class' => 'test', data-number=>123}")),
                         {'class': 'test', 'data-number': '123'})

        # Ruby style colons
        self.assertEqual(dict(self._parse("{:class => 'test', :data-number=>123}")),
                         {'class': 'test', 'data-number': '123'})

        # list attribute values
        self.assertEqual(dict(self._parse("{'class': [ 'a', 'b', 'c' ], data-list=>[1, 2, 3]}")),
                         {'class': ['a', 'b', 'c'], 'data-list': ['1', '2', '3']})

        # tuple attribute values
        self.assertEqual(dict(self._parse("{'class': ( 'a', 'b', 'c' ), data-list=>(1, 2, 3)}")),
                         {'class': ('a', 'b', 'c'), 'data-list': ('1', '2', '3')})

        # attribute order is maintained
        self.assertEqual(self._parse("{'class': 'test', 'id': 'something', foo: 'bar'}"),
                         OrderedDict([('class', 'test'), ('id', 'something'), ('foo', 'bar')]))

        # attributes values split over multiple lines
        self.assertEqual(dict(self._parse("""{
                'class':
                    - if forloop.first
                        link-first
\x20
                    - else
                        - if forloop.last
                            link-last
                'href':
                    - url 'some_view'
                }""")), {
            'class': '{% if forloop.first %} link-first {% else %} {% if forloop.last %} link-last {% endif %} {% endif %}',  # noqa
            'href': "{% url 'some_view' %}"
        })

        # non-ascii attribute values
        self.assertEqual(dict(self._parse("{class: 'test\u1234'}")), {'class': 'test\u1234'})

        # html style dicts
        self.assertEqual(dict(self._parse("(:class='test' :data-number = 123\n foo=\"bar\")")),
                         {'class': 'test', 'data-number': '123', 'foo': 'bar'})

    def test_empty_attribute_raises_error(self):
        # empty quoted string
        with self.assertRaisesRegexp(ParseException, "Empty attribute key. @ \"{'':\" <-"):
            self._parse("{'': 'test'}")

        # empty unquoted
        with self.assertRaisesRegexp(ParseException, "Empty attribute key. @ \"{: \" <-"):
            self._parse("{: 'test'}")

    def test_unterminated_string_raises_error(self):
        # on attribute key
        with self.assertRaisesRegexp(ParseException, "Unterminated string \(expected '\). @ \"{'test: 123}\" <-"):
            self._parse("{'test: 123}")

        # on attribute value
        with self.assertRaisesRegexp(ParseException, "Unterminated string \(expected \"\). @ \"{'test': \"123}\" <-"):
            self._parse("{'test': \"123}")

    def test_duplicate_attributes_raise_error(self):
        with self.assertRaisesRegexp(ParseException, "Duplicate attribute: \"class\". @ \"{class: 'test', class: 'bar'}\" <-"):  # noqa
            self._parse("{class: 'test', class: 'bar'}")

        with self.assertRaisesRegexp(ParseException, "Duplicate attribute: \"class\". @ \"\(class='test' class='bar'\)\" <-"):  # noqa
            self._parse("(class='test' class='bar')")

    def test_mixing_ruby_and_html_syntax_raises_errors(self):
        # omit comma in Ruby style dict
        with self.assertRaisesRegexp(ParseException, "Expected \",\". @ \"{class: 'test' f\" <-"):
            self._parse("{class: 'test' foo: 'bar'}")

        # use = in Ruby style dict
        with self.assertRaisesRegexp(ParseException, "Expected \"=>\" or \":\". @ \"{class=\" <-"):
            self._parse("{class='test'}")

        # use comma in HTML style dict
        with self.assertRaisesRegexp(ParseException, "Unexpected \",\". @ \"\(class='test',\" <-"):
            self._parse("(class='test', foo = 'bar')")

        # use : in HTML style dict
        with self.assertRaisesRegexp(ParseException, "Expected \"=\". @ \"\(class:\" <-"):
            self._parse("(class:'test')")

        # use => in HTML style dict
        with self.assertRaisesRegexp(ParseException, "Unexpected \">\". @ \"\(class=>\" <-"):
            self._parse("(class=>'test')")
