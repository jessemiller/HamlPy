from nose.tools import eq_

from hamlpy.attribute_dict_parser import AttributeDictParser

class TestAttributeDictParser(object):

    def test_empty_dictionary(self):
        dict=AttributeDictParser("{}").parse()
        eq_(len(dict), 0)

    def test_one_string_value(self):
        dict=AttributeDictParser("{'class': 'test'}").parse()
        eq_(dict.get('class'), 'test')

    def test_two_string_value(self):
        dict=AttributeDictParser("{'class': 'test', 'id': 'something'}").parse()
        eq_(dict.get('class'), 'test')
        eq_(dict.get('id'), 'something')

    def test_integer_value(self):
        dict=AttributeDictParser("{'class': 'test', 'data-number': 123}").parse()
        eq_(dict.get('class'), 'test')
        eq_(dict.get('data-number'), '123')

    def test_float_value(self):
        dict=AttributeDictParser("{'class': 'test', 'data-number': 123.456}").parse()
        eq_(dict.get('class'), 'test')
        eq_(dict.get('data-number'), '123.456')

    def test_none_value(self):
        dict=AttributeDictParser("{'controls': None}").parse()
        eq_(dict.get('controls'), None)

    def test_colon_in_key(self):
        dict=AttributeDictParser("{'xml:lang': 'en'}").parse()
        eq_(dict.get('xml:lang'), 'en')

    def test_colon_in_value(self):
        dict=AttributeDictParser("{'xmllang': 'e:n'}").parse()
        eq_(dict.get('xmllang'), 'e:n')

    def test_double_quotes(self):
        dict=AttributeDictParser('{"class": "test", "data-number": "123"}').parse()
        eq_(dict.get('class'), 'test')
        eq_(dict.get('data-number'), '123')

    def test_key_quotes_are_optional(self):
        dict=AttributeDictParser("{class: 'test', data-number: 123}").parse()
        eq_(dict.get('class'), 'test')
        eq_(dict.get('data-number'), '123')

    def test_whitespace_between_key_and_value(self):
        dict=AttributeDictParser("{   class:        'test',     data-number:    123}").parse()
        eq_(dict.get('class'), 'test')
        eq_(dict.get('data-number'), '123')

    def test_whitespace_before_colon(self):
        dict=AttributeDictParser("{   class \t:        'test'}").parse()
        eq_(dict.get('class'), 'test')

    def test_trailing_comma(self):
        dict=AttributeDictParser("{class: 'test', }").parse()
        eq_(dict.get('class'), 'test')

    def test_multiline_after_values(self):
        dict=AttributeDictParser("""{class: 'test',
         data-number: 123}""").parse()
        eq_(dict.get('class'), 'test')
        eq_(dict.get('data-number'), '123')

    def test_ruby_haml_arrow(self):
        dict=AttributeDictParser("{'class' => 'test'}").parse()
        eq_(dict.get('class'), 'test')

    def test_ruby_haml_colon(self):
        dict=AttributeDictParser("{ :class => 'test'}").parse()
        eq_(dict.get('class'), 'test')

    def test_list_value(self):
        dict=AttributeDictParser("{ class: ['a','b','c']}").parse()
        eq_(dict.get('class'), ['a','b','c'])

    def test_tuple_value(self):
        dict=AttributeDictParser("{ class: ('a','b','c')}").parse()
        eq_(dict.get('class'), ('a','b','c'))

    def test_attribute_value_not_quoted_when_looks_like_key(self):
        dict=AttributeDictParser('{name:"viewport", content:"width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1"}').parse()
        eq_(dict.get('content'), 'width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1')
        eq_(dict.get('name'), 'viewport')


    def test_multiline_haml_in_attributes(self):
        s="""{
        'class':
            - if forloop.first
                link-first
            - else
                - if forloop.last
                    link-last
        'href':
            - url 'some_view'
        }"""
        dict=AttributeDictParser(s).parse()
        eq_(dict.get('class'), '{% if forloop.first %} link-first {% else %} {% if forloop.last %} link-last {% endif %} {% endif %}')
        eq_(dict.get('href'), "{% url 'some_view' %}")

    # \r\n and \n
    # Curly braces in multiline HAML
    # Blank lines in Multiline HAML
    # Incorrectly indented multiline HAML
