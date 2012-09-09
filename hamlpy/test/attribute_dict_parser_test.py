from nose.tools import eq_

from hamlpy.attribute_dict_parser import AttributeDictParser

class TestAttributeDictParser(object):

    def test_empty_dictionary(self):
        dict=AttributeDictParser("{}").parse()
        eq_(len(dict), 0)
        
    def test_one_string_value(self):
        dict=AttributeDictParser("{'class': 'test'}").parse()
        eq_(dict['class'], 'test')
    
    def test_two_string_value(self):
        dict=AttributeDictParser("{'class': 'test', 'id': 'something'}").parse()
        eq_(dict['class'], 'test')
        eq_(dict['id'], 'something')
    
    def test_integer_value(self):
        dict=AttributeDictParser("{'class': 'test', 'data-number': 123}").parse()
        eq_(dict['class'], 'test')
        eq_(dict['data-number'], '123')
        
    def test_float_value(self):
        dict=AttributeDictParser("{'class': 'test', 'data-number': 123.456}").parse()
        eq_(dict['class'], 'test')
        eq_(dict['data-number'], '123.456')
        
    def test_none_value(self):
        dict=AttributeDictParser("{'controls': None}").parse()
        eq_(dict['controls'], None)
        
    def test_colon_in_key(self):
        dict=AttributeDictParser("{'xml:lang': 'en'}").parse()
        eq_(dict['xml:lang'], 'en')
    
    def test_colon_in_value(self):
        dict=AttributeDictParser("{'xmllang': 'e:n'}").parse()
        eq_(dict['xmllang'], 'e:n')
    
    def test_double_quotes(self):
        dict=AttributeDictParser('{"class": "test", "data-number": "123"}').parse()
        eq_(dict['class'], 'test')
        eq_(dict['data-number'], '123')
    
    def test_key_quotes_are_optional(self):
        dict=AttributeDictParser("{class: 'test', data-number: 123}").parse()
        eq_(dict['class'], 'test')
        eq_(dict['data-number'], '123')
        
    def test_whitespace(self):
        dict=AttributeDictParser("{   class:        'test',     data-number:    123}").parse()
        eq_(dict['class'], 'test')
        eq_(dict['data-number'], '123')
    
    def test_multiline_after_values(self):
        dict=AttributeDictParser("""{class: 'test',
         data-number: 123}""").parse()
        eq_(dict['class'], 'test')
        eq_(dict['data-number'], '123')
        
    def test_ruby_haml_arrow(self):
        dict=AttributeDictParser("{'class' => 'test'}").parse()
        eq_(dict['class'], 'test')
        
    def test_ruby_haml_colon(self):
        dict=AttributeDictParser("{ :class => 'test'}").parse()
        eq_(dict['class'], 'test')
        
    def test_list_value(self):
        dict=AttributeDictParser("{ class: ['a','b','c']}").parse()
        eq_(dict['class'], ['a','b','c'])
        
    def test_tuple_value(self):
        dict=AttributeDictParser("{ class: ('a','b','c')}").parse()
        eq_(dict['class'], ('a','b','c'))