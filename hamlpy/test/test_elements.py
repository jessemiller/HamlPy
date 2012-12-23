from nose.tools import eq_

from hamlpy.elements import Element

class TestElement(object):

        def test_attribute_value_not_quoted_when_looks_like_key(self):
            sut = Element('')
            s1 = sut._parse_attribute_dictionary('''{name:"viewport", content:"width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1"}''')
            eq_(s1['content'], 'width:device-width, initial-scale:1, minimum-scale:1, maximum-scale:1')
            eq_(s1['name'], 'viewport')

            sut = Element('')
            s1 = sut._parse_attribute_dictionary('''{style:"a:x, b:'y', c:1, e:3"}''')
            eq_(s1['style'], "a:x, b:'y', c:1, e:3")

            sut = Element('')
            s1 = sut._parse_attribute_dictionary('''{style:"a:x, b:'y', c:1, d:\\"dk\\", e:3"}''')
            eq_(s1['style'], '''a:x, b:'y', c:1, d:"dk", e:3''')

            sut = Element('')
            s1 = sut._parse_attribute_dictionary('''{style:'a:x, b:\\'y\\', c:1, d:"dk", e:3'}''')
            eq_(s1['style'], '''a:x, b:'y', c:1, d:"dk", e:3''')

        def test_dashes_work_in_attribute_quotes(self):
            sut = Element('')
            s1 = sut._parse_attribute_dictionary('''{"data-url":"something", "class":"blah"}''')
            eq_(s1['data-url'],'something')
            eq_(s1['class'], 'blah')

            s1 = sut._parse_attribute_dictionary('''{data-url:"something", class:"blah"}''')
            eq_(s1['data-url'],'something')
            eq_(s1['class'], 'blah')

        def test_escape_quotes_except_django_tags(self):
            sut = Element('')

            s1 = sut._escape_attribute_quotes('''{% url 'blah' %}''')
            eq_(s1,'''{% url 'blah' %}''')

            s2 = sut._escape_attribute_quotes('''blah's blah''s {% url 'blah' %} blah's blah''s''')
            eq_(s2,r"blah\'s blah\'\'s {% url 'blah' %} blah\'s blah\'\'s")

        def test_attributes_parse(self):
            sut = Element('')

            s1 = sut._parse_attribute_dictionary('''{a:'something',"b":None,'c':2}''')
            eq_(s1['a'],'something')
            eq_(s1['b'],None)
            eq_(s1['c'],2)

            eq_(sut.attributes, "a='something' c='2' b")

        def test_pulls_tag_name_off_front(self):
            sut = Element('%div.class')
            eq_(sut.tag, 'div')
            
        def test_default_tag_is_div(self):
            sut = Element('.class#id')
            eq_(sut.tag, 'div')
            
        def test_parses_id(self):
            sut = Element('%div#someId.someClass')
            eq_(sut.id, 'someId')
            
            sut = Element('#someId.someClass')
            eq_(sut.id, 'someId')
            
        def test_no_id_gives_empty_string(self):
            sut = Element('%div.someClass')
            eq_(sut.id, '')
        
        def test_parses_class(self):
            sut = Element('%div#someId.someClass')
            eq_(sut.classes, 'someClass')
            
        def test_properly_parses_multiple_classes(self):
            sut = Element('%div#someId.someClass.anotherClass')
            eq_(sut.classes, 'someClass anotherClass')
            
        def test_no_class_gives_empty_string(self):
            sut = Element('%div#someId')
            eq_(sut.classes, '')
            
        def test_attribute_dictionary_properly_parses(self):
            sut = Element("%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}")
            assert "xmlns='http://www.w3.org/1999/xhtml'" in sut.attributes
            assert "xml:lang='en'" in sut.attributes
            assert "lang='en'" in sut.attributes

        def test_id_and_class_dont_go_in_attributes(self):
            sut = Element("%div{'class':'hello', 'id':'hi'}")
            assert 'class=' not in sut.attributes
            assert 'id=' not in sut.attributes
            
        def test_attribute_merges_classes_properly(self):
            sut = Element("%div.someClass.anotherClass{'class':'hello'}")
            assert 'someClass' in sut.classes
            assert 'anotherClass' in sut.classes
            assert 'hello' in sut.classes
            
        def test_attribute_merges_ids_properly(self):
            sut = Element("%div#someId{'id':'hello'}")
            eq_(sut.id, 'someId_hello')
            
        def test_can_use_arrays_for_id_in_attributes(self):
            sut = Element("%div#someId{'id':['more', 'andMore']}")
            eq_(sut.id, 'someId_more_andMore')
        
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
            assert sut.django_variable == False
            
        def test_grabs_inline_tag_content(self):
            sut = Element("%div Some Text")
            eq_(sut.inline_content, 'Some Text')
            
        def test_multiline_attributes(self):
            sut = Element("""%link{'rel': 'stylesheet', 'type': 'text/css',
                'href': '/long/url/to/stylesheet/resource.css'}""")
            assert "href='/long/url/to/stylesheet/resource.css'" in sut.attributes
            assert "type='text/css'" in sut.attributes
            assert "rel='stylesheet'" in sut.attributes

        def test_conditional_arguments(self):
            sut = Element("""%a{
                'href': 'profile' if request.user.is_authenticated else 'login',
                'data-login': '={request.user.login}' if request.user.is_authenticated,
                'class': 'at-least-three' if x >= 3 else 'less-than-three'
            }""")
            assert """{% if request.user.is_authenticated %}href='profile'{% else %}href='login'{% endif %}""" in sut.attributes
            assert """{% if request.user.is_authenticated %}data-login='={request.user.login}'{% endif %}""" in sut.attributes
            assert """{% if x>=3 %}at-least-three{% else %}less-than-three{% endif %}""" in sut.classes
