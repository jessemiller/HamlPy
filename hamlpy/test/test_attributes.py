import unittest

from collections import OrderedDict

from hamlpy.compiler import Compiler
from hamlpy.parser.attributes import read_attribute_dict
from hamlpy.parser.core import Stream, ParseException


class AttributeDictParserTest(unittest.TestCase):

    @staticmethod
    def _parse(text):
        return read_attribute_dict(Stream(text), Compiler())

    def test_read_ruby_style_attribute_dict(self):
        # empty dict
        stream = Stream("{}><")
        assert dict(read_attribute_dict(stream, Compiler())) == {}
        assert stream.text[stream.ptr:] == '><'

        # string values
        assert dict(self._parse("{'class': 'test'} =Test")) == {'class': 'test'}
        assert dict(self._parse("{'class': 'test', 'id': 'something'}")) == {'class': 'test', 'id': 'something'}

        # integer values
        assert dict(self._parse("{'data-number': 0}")) == {'data-number': '0'}
        assert dict(self._parse("{'data-number': 12345}")) == {'data-number': '12345'}

        # float values
        assert dict(self._parse("{'data-number': 123.456}")) == {'data-number': '123.456'}
        assert dict(self._parse("{'data-number': 0.001}")) == {'data-number': '0.001'}

        # None value
        assert dict(self._parse("{'controls': None}")) == {'controls': None}

        # boolean attributes
        assert dict(self._parse(
            "{disabled, class:'test', data-number : 123,\n foo:\"bar\"}"
        )) == {'disabled': True, 'class': 'test', 'data-number': '123', 'foo': 'bar'}

        assert dict(self._parse(
            "{class:'test', data-number : 123,\n foo:\"bar\",  \t   disabled}"
        )) == {'disabled': True, 'class': 'test', 'data-number': '123', 'foo': 'bar'}

        # attribute name has colon
        assert dict(self._parse("{'xml:lang': 'en'}")) == {'xml:lang': 'en'}

        # attribute value has colon or commas
        assert dict(self._parse("{'lang': 'en:g'}")) == {'lang': 'en:g'}
        assert dict(self._parse(
            '{name:"viewport", content:"width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1"}'
        )) == {'name': 'viewport', 'content': 'width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1'}

        # double quotes
        assert dict(self._parse('{"class": "test", "id": "something"}')) == {'class': 'test', 'id': 'something'}

        # no quotes for key
        assert dict(self._parse("{class: 'test', id: 'something'}")) == {'class': 'test', 'id': 'something'}

        # whitespace is ignored
        assert dict(self._parse(
            "{   class  \t :        'test',     data-number:    123  }"
        )) == {'class': 'test', 'data-number': '123'}

        # trailing commas are fine
        assert dict(self._parse("{class: 'test', data-number: 123,}")) == {'class': 'test', 'data-number': '123'}

        # attributes split onto multiple lines
        assert dict(self._parse("{class: 'test',\n     data-number: 123}")) == {'class': 'test', 'data-number': '123'}

        # old style Ruby
        assert dict(self._parse("{:class => 'test', :data-number=>123}")) == {'class': 'test', 'data-number': '123'}

        # list attribute values
        assert dict(self._parse(
            "{'class': [ 'a', 'b', 'c' ], data-list:[1, 2, 3]}"
        )) == {'class': ['a', 'b', 'c'], 'data-list': ['1', '2', '3']}

        # tuple attribute values
        assert dict(self._parse(
            "{:class=>( 'a', 'b', 'c' ), :data-list => (1, 2, 3)}"
        )) == {'class': ['a', 'b', 'c'], 'data-list': ['1', '2', '3']}

        # attribute order is maintained
        assert self._parse(
            "{'class': 'test', 'id': 'something', foo: 'bar'}"
        ) == OrderedDict([('class', 'test'), ('id', 'something'), ('foo', 'bar')])

        # attribute values can be multi-line Haml
        assert dict(self._parse("""{
                'class':
                    - if forloop.first
                        link-first
\x20
                    - else
                        - if forloop.last
                            link-last
                'href':
                    - url 'some_view'
                }"""
        )) == {
            'class': '{% if forloop.first %} link-first {% else %} {% if forloop.last %} link-last {% endif %} {% endif %}',  # noqa
            'href': "{% url 'some_view' %}"
        }

        # non-ascii attribute values
        assert dict(self._parse("{class: 'test\u1234'}")) == {'class': 'test\u1234'}

    def test_read_html_style_attribute_dict(self):
        # html style dicts
        assert dict(self._parse("()><")) == {}
        assert dict(self._parse("(   )")) == {}

        # string values
        assert dict(self._parse("(class='test') =Test")) == {'class': 'test'}
        assert dict(self._parse("(class='test' id='something')")) == {'class': 'test', 'id': 'something'}

        # integer values
        assert dict(self._parse("(data-number=0)")) == {'data-number': '0'}
        assert dict(self._parse("(data-number=12345)")) == {'data-number': '12345'}

        # float values
        assert dict(self._parse("(data-number=123.456)")) == {'data-number': '123.456'}
        assert dict(self._parse("(data-number=0.001)")) == {'data-number': '0.001'}

        # None value
        assert dict(self._parse("(controls=None)")) == {'controls': None}

        # boolean attributes
        assert dict(self._parse(
            "(disabled class='test' data-number = 123\n foo=\"bar\")"
        )) == {'disabled': True, 'class': 'test', 'data-number': '123', 'foo': 'bar'}

        assert dict(self._parse(
            "(class='test' data-number = 123\n foo=\"bar\"  \t   disabled)"
        )) == {'disabled': True, 'class': 'test', 'data-number': '123', 'foo': 'bar'}

        # attribute name has colon
        assert dict(self._parse('(xml:lang="en")')) == {'xml:lang': 'en'}

        # attribute names with characters found in JS frameworks
        assert dict(self._parse('([foo]="a" ?foo$="b")')) == {'[foo]': 'a', '?foo$': 'b'}

        # double quotes
        assert dict(self._parse('(class="test" id="something")')) == {'class': 'test', 'id': 'something'}

        # list attribute values
        assert dict(self._parse(
            "(class=[ 'a', 'b', 'c' ] data-list=[1, 2, 3])"
        )) == {'class': ['a', 'b', 'c'], 'data-list': ['1', '2', '3']}

        # variable attribute values
        assert dict(self._parse('(foo=bar)')) == {'foo': '{{ bar }}'}

        # attribute values can be multi-line Haml
        assert dict(self._parse("""(
                class=
                    - if forloop.first
                        link-first
\x20
                    - else
                        - if forloop.last
                            link-last
                href=
                    - url 'some_view'
                )"""
                        )) == {
           'class': '{% if forloop.first %} link-first {% else %} {% if forloop.last %} link-last {% endif %} {% endif %}',  # noqa
           'href': "{% url 'some_view' %}"
       }

    def test_empty_attribute_name_raises_error(self):
        # empty quoted string in Ruby new style
        with self.assertRaisesRegex(ParseException, r'Attribute name can\'t be an empty string. @ "{\'\':" <-'):
            self._parse("{'': 'test'}")

        # empty old style Ruby attribute
        with self.assertRaisesRegex(ParseException, r'Unexpected " ". @ "{: " <-'):
            self._parse("{: 'test'}")

        # missing (HTML style)
        with self.assertRaisesRegex(ParseException, r'Unexpected "=". @ "\(=" <-'):
            self._parse("(='test')")
        with self.assertRaisesRegex(ParseException, r'Unexpected "=". @ "\(foo=\'bar\' =" <-'):
            self._parse("(foo='bar' ='test')")

    def test_empty_attribute_value_raises_error(self):
        with self.assertRaisesRegex(ParseException, r'Unexpected "}". @ "{:class=>}" <-'):
            self._parse("{:class=>}")
        with self.assertRaisesRegex(ParseException, r'Unexpected "}". @ "{class:}" <-'):
            self._parse("{class:}")
        with self.assertRaisesRegex(ParseException, r'Unexpected "\)". @ "\(class=\)" <-'):
            self._parse("(class=)")

    def test_unterminated_string_raises_error(self):
        # on attribute key
        with self.assertRaisesRegex(ParseException, r'Unterminated string \(expected \'\). @ "{\'test: 123}" <-'):
            self._parse("{'test: 123}")

        # on attribute value
        with self.assertRaisesRegex(ParseException, r'Unterminated string \(expected "\). @ "{\'test\': "123}" <-'):
            self._parse("{'test': \"123}")

    def test_duplicate_attributes_raise_error(self):
        with self.assertRaisesRegex(ParseException, r'Duplicate attribute: "class". @ "{class: \'test\', class: \'bar\'}" <-'):  # noqa
            self._parse("{class: 'test', class: 'bar'}")

        with self.assertRaisesRegex(ParseException, r'Duplicate attribute: "class". @ "\(class=\'test\' class=\'bar\'\)" <-'):  # noqa
            self._parse("(class='test' class='bar')")

    def test_mixing_ruby_and_html_syntax_raises_errors(self):
        # omit comma in Ruby style dict
        with self.assertRaisesRegex(ParseException, r'Expected ",". @ "{class: \'test\' f" <-'):
            self._parse("{class: 'test' foo: 'bar'}")

        # use = in Ruby style dict
        with self.assertRaisesRegex(ParseException, r'Expected ":". @ "{class=" <-'):
            self._parse("{class='test'}")
        with self.assertRaisesRegex(ParseException, r'Expected "=>". @ "{:class=" <-'):
            self._parse("{:class='test'}")

        # use colon as assignment for old style Ruby attribute
        with self.assertRaisesRegex(ParseException, r'Expected "=>". @ "{:class:" <-'):
            self._parse("{:class:'test'}")

        # use comma in HTML style dict
        with self.assertRaisesRegex(ParseException, r'Unexpected ",". @ "\(class=\'test\'," <-'):
            self._parse("(class='test', foo = 'bar')")

        # use : for assignment in HTML style dict (will treat as part of attribute name)
        with self.assertRaisesRegex(ParseException, r'Unexpected "\'". @ "\(class:\'" <-'):
            self._parse("(class:'test')")

        # use attribute quotes in HTML style dict
        with self.assertRaisesRegex(ParseException, r'Unexpected "\'". @ "\(\'" <-'):
            self._parse("('class'='test')")

        # use => in HTML style dict
        with self.assertRaisesRegex(ParseException, r'Unexpected ">". @ "\(class=>" <-'):
            self._parse("(class=>'test')")

        # use tuple syntax in HTML style dict
        with self.assertRaisesRegex(ParseException, r'Unexpected "\(". @ "\(class=\(" <-'):
            self._parse("(class=(1, 2))")

    def test_unexpected_eof(self):
        with self.assertRaisesRegex(ParseException, r'Unexpected end of input. @ "{:class=>" <-'):
            self._parse("{:class=>")
        with self.assertRaisesRegex(ParseException, r'Unexpected end of input. @ "{class:" <-'):
            self._parse("{class:")
        with self.assertRaisesRegex(ParseException, r'Unexpected end of input. @ "\(class=" <-'):
            self._parse("(class=")
