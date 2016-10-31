from __future__ import unicode_literals

import unittest

from collections import OrderedDict
from hamlpy.attribute_dict_parser import AttributeDictParser


class AttributeDictParserTest(unittest.TestCase):

    @staticmethod
    def _parse(text):
        return AttributeDictParser(text).parse()

    def test_parse(self):
        # TODO
        # \r\n and \n
        # Curly braces in multiline HAML
        # Blank lines in Multiline HAML
        # Incorrectly indented multiline HAML

        # empty dict
        self.assertEqual(dict(self._parse("{}")), {})

        # string values
        self.assertEqual(dict(self._parse("{'class': 'test'}")), {'class': 'test'})
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
        self.assertEqual(dict(self._parse('{name:"viewport", content:"width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1"}')),
                         {'name': 'viewport', 'content': 'width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1'})

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
                    - else
                        - if forloop.last
                            link-last
                'href':
                    - url 'some_view'
                }""")), {
            'class': '{% if forloop.first %} link-first {% else %} {% if forloop.last %} link-last {% endif %} {% endif %}',
            'href': "{% url 'some_view' %}"
        })

        # non-ascii attribute values
        self.assertEqual(dict(self._parse("{class: 'test\u1234'}")), {'class': 'test\u1234'})
