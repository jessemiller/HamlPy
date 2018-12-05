import unittest

from collections import OrderedDict

from hamlpy.compiler import Compiler
from hamlpy.parser.core import Stream
from hamlpy.parser.elements import Element, read_tag, read_element


class ElementTest(unittest.TestCase):

    def test_read_tag(self):
        stream = Stream('angular:ng-repeat(')
        self.assertEqual(read_tag(stream), 'angular:ng-repeat')
        self.assertEqual(stream.text[stream.ptr:], '(')

    def test_read_element(self):
        stream = Stream('%angular:ng-repeat.my-class#my-id(class="test")></=  Hello  \n.next-element')
        element = read_element(stream, Compiler())
        self.assertEqual(element.tag, 'angular:ng-repeat')
        self.assertEqual(element.id, 'my-id')
        self.assertEqual(element.classes, ['test', 'my-class'])
        self.assertEqual(dict(element.attributes), {'class': "test"})
        self.assertEqual(element.nuke_outer_whitespace, True)
        self.assertEqual(element.nuke_inner_whitespace, True)
        self.assertEqual(element.self_close, True)
        self.assertEqual(element.django_variable, True)
        self.assertEqual(element.inline_content, "Hello")
        self.assertEqual(stream.text[stream.ptr:], '.next-element')

        stream = Stream('%input{required}  ')
        element = read_element(stream, Compiler())
        self.assertEqual(element.tag, 'input')
        self.assertEqual(element.id, None)
        self.assertEqual(element.classes, [])
        self.assertEqual(dict(element.attributes), {'required': True})
        self.assertEqual(element.nuke_outer_whitespace, False)
        self.assertEqual(element.nuke_inner_whitespace, False)
        self.assertEqual(element.self_close, True)  # input is implicitly self-closing
        self.assertEqual(element.django_variable, False)
        self.assertEqual(element.inline_content, '')
        self.assertEqual(stream.text[stream.ptr:], '')

    def test_escape_attribute_quotes(self):
        s1 = Element._escape_attribute_quotes('''{% url 'blah' %}''', attr_wrapper="'")
        assert s1 == '''{% url 'blah' %}'''

        s2 = Element._escape_attribute_quotes('''blah's blah''s {% url 'blah' %} blah's blah''s''', attr_wrapper="'")
        assert s2 == r"blah\'s blah\'\'s {% url 'blah' %} blah\'s blah\'\'s"

    def test_parses_tag(self):
        element = self._read_element('%span.class')
        assert element.tag == 'span'

        # can have namespace and hypens
        element = self._read_element('%ng-tags:ng-repeat.class')
        assert element.tag == 'ng-tags:ng-repeat'

        # defaults to div
        element = self._read_element('.class#id')
        assert element.tag == 'div'

    def test_parses_id(self):
        element = self._read_element('%div#someId.someClass')
        assert element.id == 'someId'

        element = self._read_element('#someId.someClass')
        assert element.id == 'someId'

        element = self._read_element('%div.someClass')
        assert element.id is None

    def test_parses_classes(self):
        element = self._read_element('%div#someId.someClass')
        assert element.classes == ['someClass']

        element = self._read_element('%div#someId.someClass.anotherClass')
        assert element.classes == ['someClass', 'anotherClass']

        # classes before id
        element = self._read_element('%div.someClass.anotherClass#someId')
        assert element.classes == ['someClass', 'anotherClass']

        # classes can contain hypens and underscores
        element = self._read_element('%div.-some-class-._another_class_')
        assert element.classes == ['-some-class-', '_another_class_']

        # no class
        element = self._read_element('%div#someId')
        assert element.classes == []

    def test_attribute_dictionary_properly_parses(self):
        element = self._read_element("%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}")

        assert element.attributes == OrderedDict([
            ('xmlns', "http://www.w3.org/1999/xhtml"),
            ('xml:lang', "en"),
            ('lang', "en")
        ])

    def test_attribute_merges_classes_properly(self):
        element = self._read_element("%div.someClass.anotherClass{'class':'hello'}")

        assert element.classes == ['hello', 'someClass', 'anotherClass']

    def test_attribute_merges_ids_properly(self):
        element = self._read_element("%div#someId{'id':'hello'}")
        assert element.id == 'someId_hello'

    def test_can_use_arrays_for_id_in_attributes(self):
        element = self._read_element("%div#someId{'id':['more', 'andMore']}")
        assert element.id == 'someId_more_andMore'

    def test_self_closes_a_self_closing_tag(self):
        element = self._read_element(r"%br")
        assert element.self_close

    def test_does_not_close_a_non_self_closing_tag(self):
        element = self._read_element("%div")
        assert element.self_close is False

    def test_can_close_a_non_self_closing_tag(self):
        element = self._read_element("%div/")
        assert element.self_close

    def test_properly_detects_django_tag(self):
        element = self._read_element("%div= $someVariable")
        assert element.django_variable

    def test_knows_when_its_not_django_tag(self):
        element = self._read_element("%div Some Text")
        assert element.django_variable is False

    def test_grabs_inline_tag_content(self):
        element = self._read_element("%div Some Text")
        assert element.inline_content == 'Some Text'

        element = self._read_element("%div {% trans 'hello' %}")
        assert element.inline_content == "{% trans 'hello' %}"

    def test_multiline_attributes(self):
        element = self._read_element("""%link{'rel': 'stylesheet', 'type': 'text/css',
            'href': '/long/url/to/stylesheet/resource.css'}""")

        assert element.attributes == OrderedDict([
            ('rel', "stylesheet"),
            ('type', "text/css"),
            ('href', "/long/url/to/stylesheet/resource.css")
        ])

    @staticmethod
    def _read_element(text):
        return read_element(Stream(text), Compiler())
