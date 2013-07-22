from nose.tools import eq_
from hamlpy.elements import Element


class TestElement(object):

    def test_attribute_value_not_quoted_when_looks_like_key(self):
        sut = Element('')
        s1 = sut._parse_attribute_dictionary('''(name="viewport" content="width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1")''')
        eq_(s1['content'], 'width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1')
        eq_(s1['name'], 'viewport')


        sut = Element('')
        s1 = sut._parse_attribute_dictionary('''(style="a:x, b:'y', c:1, e:3")''')
        eq_(s1['style'], "a:x, b:'y', c:1, e:3")

        # Escaping haven't realized
        # sut = Element('')
        # s1 = sut._parse_attribute_dictionary('''(style="a:x, b:'y', c:1, d:\\"dk\\", e:3")''')
        # eq_(s1['style'], '''a:x, b:'y', c:1, d:"dk", e:3''')

        # sut = Element('')
        # s1 = sut._parse_attribute_dictionary('''(style='a:x, b:\\'y\\', c:1, d:"dk", e:3')''')
        # eq_(s1['style'], '''a:x, b:'y', c:1, d:"dk", e:3''')

    def test_dashes_work_in_attribute_quotes(self):
        sut = Element('')
        s1 = sut._parse_attribute_dictionary('''("data-url"="something" "class"="blah")''')
        eq_(s1['data-url'],'something')
        eq_(s1['class'], 'blah')

        s1 = sut._parse_attribute_dictionary('''("data-url"="something" class="blah")''')
        eq_(s1['data-url'],'something')
        eq_(s1['class'], 'blah')


    def test_dashes_work_in_attribute_without_quotes(self):
        sut = Element('')
        s1 = sut._parse_attribute_dictionary('''(data-url="something" "class"="blah")''')
        eq_(s1['data-url'],'something')
        eq_(s1['class'], 'blah')

        s1 = sut._parse_attribute_dictionary('''(data-url="something" class="blah")''')
        eq_(s1['data-url'],'something')
        eq_(s1['class'], 'blah')


    def test_attribute_dictionary_properly_parses(self):
        sut = Element("%html(xmlns='http://www.w3.org/1999/xhtml' 'xml:lang'='en'  'lang'='en') :)))")
        print sut.attributes
        assert "xmlns='http://www.w3.org/1999/xhtml'" in sut.attributes
        assert "xml:lang='en'" in sut.attributes
        assert "lang='en'" in sut.attributes


    def test_id_and_class_dont_go_in_attributes(self):
        sut = Element("%div('class'='hello' 'id'='hi')")
        assert 'class=' not in sut.attributes
        assert 'id=' not in sut.attributes

    def test_attribute_merges_classes_properly(self):
        sut = Element("%div.someClass.anotherClass('class'='hello')")
        assert 'someClass' in sut.classes
        assert 'anotherClass' in sut.classes
        assert 'hello' in sut.classes

    def test_attribute_merges_ids_properly(self):
        sut = Element("%div#someId('id'='hello')")
        eq_(sut.id, 'someId_hello')

    def test_can_use_arrays_for_id_in_attributes(self):
        return
        # Not implemented
        sut = Element("%div#someId{'id':['more', 'andMore']}")
        eq_(sut.id, 'someId_more_andMore')

    def test_multiline_attributes(self):
        sut = Element("""%link('rel'='stylesheet' 'type'='text/css'
                'href'='/long/url/to/stylesheet/resource.css')""")
        print sut.attributes
        assert "href='/long/url/to/stylesheet/resource.css'" in sut.attributes
        assert "type='text/css'" in sut.attributes
        assert "rel='stylesheet'" in sut.attributes

    def test_multiline_attributes2(self):

        sut = Element("""%link(rel=stylesheet type=text/css
                href=/long/url/to/stylesheet/resource.css)""")
        assert "href='/long/url/to/stylesheet/resource.css'" in sut.attributes
        assert "type='text/css'" in sut.attributes
        assert "rel='stylesheet'" in sut.attributes

    def test_attributes_without_quotes(self):
        sut = Element("""%html(xmlns=http://www.w3.org/1999/xhtml xml:lang=en lang=en)""")
        assert "xmlns='http://www.w3.org/1999/xhtml'" in sut.attributes
        assert "xml:lang='en'" in sut.attributes
        assert "lang='en'" in sut.attributes