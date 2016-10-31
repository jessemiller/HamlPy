from __future__ import print_function, unicode_literals

import unittest

from hamlpy.elements import Element


class ElementTest(unittest.TestCase):

    def test_escape_attribute_quotes(self):
        sut = Element('')

        s1 = sut._escape_attribute_quotes('''{% url 'blah' %}''')
        assert s1 == '''{% url 'blah' %}'''

        s2 = sut._escape_attribute_quotes('''blah's blah''s {% url 'blah' %} blah's blah''s''')
        assert s2 == r"blah\'s blah\'\'s {% url 'blah' %} blah\'s blah\'\'s"

    def test_pulls_tag_name_off_front(self):
        sut = Element('%div.class')
        assert sut.tag == 'div'

    def test_default_tag_is_div(self):
        sut = Element('.class#id')
        assert sut.tag == 'div'

    def test_parses_id(self):
        sut = Element('%div#someId.someClass')
        assert sut.id == 'someId'

        sut = Element('#someId.someClass')
        assert sut.id == 'someId'

    def test_no_id_gives_empty_string(self):
        sut = Element('%div.someClass')
        assert sut.id == ''

    def test_parses_class(self):
        sut = Element('%div#someId.someClass')
        assert sut.classes == 'someClass'

    def test_properly_parses_multiple_classes(self):
        sut = Element('%div#someId.someClass.anotherClass')
        assert sut.classes == 'someClass anotherClass'

    def test_no_class_gives_empty_string(self):
        sut = Element('%div#someId')
        assert sut.classes == ''

    def test_attribute_dictionary_properly_parses(self):
        sut = Element("%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}")
        assert "xmlns='http://www.w3.org/1999/xhtml'" in sut.attributes
        assert "xml:lang='en'" in sut.attributes
        assert "lang='en'" in sut.attributes

    def test_attribute_merges_classes_properly(self):
        sut = Element("%div.someClass.anotherClass{'class':'hello'}")
        assert 'someClass' in sut.classes
        assert 'anotherClass' in sut.classes
        assert 'hello' in sut.classes

    def test_attribute_merges_ids_properly(self):
        sut = Element("%div#someId{'id':'hello'}")
        assert sut.id == 'someId_hello'

    def test_can_use_arrays_for_id_in_attributes(self):
        sut = Element("%div#someId{'id':['more', 'andMore']}")
        assert sut.id == 'someId_more_andMore'

    def test_self_closes_a_self_closing_tag(self):
        sut = Element(r"%br")
        assert sut.self_close

    def test_does_not_close_a_non_self_closing_tag(self):
        sut = Element("%div")
        assert sut.self_close == False

    def test_can_close_a_non_self_closing_tag(self):
        sut = Element("%div/")
        assert sut.self_close

    def test_properly_detects_django_tag(self):
        sut = Element("%div= $someVariable")
        assert sut.django_variable

    def test_knows_when_its_not_django_tag(self):
        sut = Element("%div Some Text")
        assert sut.django_variable is False

    def test_grabs_inline_tag_content(self):
        sut = Element("%div Some Text")
        assert sut.inline_content == 'Some Text'

    def test_multiline_attributes(self):
        sut = Element("""%link{'rel': 'stylesheet', 'type': 'text/css',
            'href': '/long/url/to/stylesheet/resource.css'}""")
        assert "href='/long/url/to/stylesheet/resource.css'" in sut.attributes
        assert "type='text/css'" in sut.attributes
        assert "rel='stylesheet'" in sut.attributes
