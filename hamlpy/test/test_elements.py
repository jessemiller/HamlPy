from __future__ import print_function, unicode_literals

import unittest

from collections import OrderedDict

from hamlpy.parser.elements import Element


class ElementTest(unittest.TestCase):

    def test_escape_attribute_quotes(self):
        s1 = Element._escape_attribute_quotes('''{% url 'blah' %}''', attr_wrapper="'")
        assert s1 == '''{% url 'blah' %}'''

        s2 = Element._escape_attribute_quotes('''blah's blah''s {% url 'blah' %} blah's blah''s''', attr_wrapper="'")
        assert s2 == r"blah\'s blah\'\'s {% url 'blah' %} blah\'s blah\'\'s"

    def test_parses_tag(self):
        element = Element.parse('%span.class')
        assert element.tag == 'span'

        # can have namespace and hypens
        element = Element.parse('%ng-tags:ng-repeat.class')
        assert element.tag == 'ng-tags:ng-repeat'

        # defaults to div
        element = Element.parse('.class#id')
        assert element.tag == 'div'

    def test_parses_id(self):
        element = Element.parse('%div#someId.someClass')
        assert element.id == 'someId'

        element = Element.parse('#someId.someClass')
        assert element.id == 'someId'

        element = Element.parse('%div.someClass')
        assert element.id is None

    def test_parses_classes(self):
        element = Element.parse('%div#someId.someClass')
        assert element.classes == ['someClass']

        element = Element.parse('%div#someId.someClass.anotherClass')
        assert element.classes == ['someClass', 'anotherClass']

        # classes before id
        element = Element.parse('%div.someClass.anotherClass#someId')
        assert element.classes == ['someClass', 'anotherClass']

        # classes can contain hypens and underscores
        element = Element.parse('%div.-some-class-._another_class_')
        assert element.classes == ['-some-class-', '_another_class_']

        # no class
        element = Element.parse('%div#someId')
        assert element.classes == []

    def test_attribute_dictionary_properly_parses(self):
        element = Element.parse("%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}")

        assert element.attributes == OrderedDict([
            ('xmlns', "http://www.w3.org/1999/xhtml"),
            ('xml:lang', "en"),
            ('lang', "en")
        ])

    def test_attribute_merges_classes_properly(self):
        element = Element.parse("%div.someClass.anotherClass{'class':'hello'}")

        assert element.classes == ['someClass', 'anotherClass', 'hello']

    def test_attribute_merges_ids_properly(self):
        element = Element.parse("%div#someId{'id':'hello'}")
        assert element.id == 'someId_hello'

    def test_can_use_arrays_for_id_in_attributes(self):
        element = Element.parse("%div#someId{'id':['more', 'andMore']}")
        assert element.id == 'someId_more_andMore'

    def test_self_closes_a_self_closing_tag(self):
        element = Element.parse(r"%br")
        assert element.self_close

    def test_does_not_close_a_non_self_closing_tag(self):
        element = Element.parse("%div")
        assert element.self_close is False

    def test_can_close_a_non_self_closing_tag(self):
        element = Element.parse("%div/")
        assert element.self_close

    def test_properly_detects_django_tag(self):
        element = Element.parse("%div= $someVariable")
        assert element.django_variable

    def test_knows_when_its_not_django_tag(self):
        element = Element.parse("%div Some Text")
        assert element.django_variable is False

    def test_grabs_inline_tag_content(self):
        element = Element.parse("%div Some Text")
        assert element.inline_content == 'Some Text'

    def test_multiline_attributes(self):
        element = Element.parse("""%link{'rel': 'stylesheet', 'type': 'text/css',
            'href': '/long/url/to/stylesheet/resource.css'}""")

        assert element.attributes == OrderedDict([
            ('rel', "stylesheet"),
            ('type', "text/css"),
            ('href', "/long/url/to/stylesheet/resource.css")
        ])
