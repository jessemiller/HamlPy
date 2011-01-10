import unittest
from nose.tools import eq_, raises
from hamlpy import hamlpy

class HamlPyTest(unittest.TestCase):
        
    def test_applies_id_properly(self):
        haml = '%div#someId Some text'
        html = "<div id='someId'>Some text</div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result.replace('\n', ''))
        
    def test_applies_class_properly(self):
        haml = '%div.someClass Some text'
        html = "<div class='someClass'>Some text</div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result.replace('\n', ''))
        
    def test_applies_multiple_classes_properly(self):
        haml = '%div.someClass.anotherClass Some text'
        html = "<div class='someClass anotherClass'>Some text</div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result.replace('\n', ''))

    def test_dictionaries_define_attributes(self):
        haml = "%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertTrue("<html" in result)
        self.assertTrue("xmlns='http://www.w3.org/1999/xhtml'" in result)
        self.assertTrue("xml:lang='en'" in result)
        self.assertTrue("lang='en'" in result)
        self.assertTrue(result.endswith("></html>") or result.endswith("></html>\n"))
    
    def test_dictionaries_support_arrays_for_id(self):
        haml = "%div{'id':('itemType', '5')}"
        html = "<div id='itemType_5'></div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result.replace('\n', ''))  
          
    def test_html_comments_rendered_properly(self):
        haml = '/ some comment'
        html = "<!-- some comment -->"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
        
    def test_django_variables_on_tag_render_properly(self):
        haml = '%div= story.tease'
        html = '<div>{{ story.tease }}</div>'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
        
    def test_web2py_variables_on_tag_render_properly(self):
        haml = '%div= story.tease'
        html = '<div>{{ =story.tease }}</div>'
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
    
    def test_web2py_variables_fncall_on_tag_render_properly(self):
        haml = '%div= story.get_absolute_url()'
        html = '<div>{{ =story.get_absolute_url() }}</div>'
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
    
    def test_stand_alone_django_variables_render(self):
        haml = '= story.tease'
        html = '{{ story.tease }}'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
        
    def test_stand_alone_web2py_variables_render(self):
        haml = '= story.tease'
        html = '{{ =story.tease }}'
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
        
    def test_stand_alone_web2py_variables_fncall_render(self):
        haml = '= story.tease()'
        html = '{{ =story.tease() }}'
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
    
    def test_stand_alone_django_tags_render(self):
        haml = '- extends "something.html"'
        html = '{% extends "something.html" %}'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
        
    def test_stand_alone_web2py_tags_render(self):
        haml = '- extend "something.html"'
        html = '{{ extend "something.html" }}'
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
        
    def test_block_web2py_tags_render(self):
        haml = '- block test\n %p hello'
        html = '{{ block test }}\n <p>hello</p>\n{{ end }}\n'
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result)
        
    def test_if_else_django_tags_render(self):
        haml = '- if something\n   %p hello\n- else\n   %p goodbye'
        html = '{% if something %}\n   <p>hello</p>\n{% else %}\n   <p>goodbye</p>\n\n{% endif %}\n'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)
        
    def test_if_else_web2py_tags_render(self):
        haml = '- if something:\n   %p hello\n- else:\n   %p goodbye'
        html = '{{ if something: }}\n   <p>hello</p>\n{{ else: }}\n   <p>goodbye</p>\n\n{{ pass }}\n'
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result)
    
    @raises(TypeError)   
    def test_throws_exception_when_trying_to_close_django(self):
        haml = '- endfor'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
    
    @raises(TypeError)    
    def test_throws_exception_when_trying_to_close_web2py(self):
        haml = '- end'
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
    
    def test_handles_dash_in_class_name_properly(self):
        haml = '.header.span-24.last'
        html = "<div class='header span-24 last'></div>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)
        
    def test_handles_multiple_attributes_in_dict(self):
        haml = "%div{'id': ('article', '3'), 'class': ('newest', 'urgent')} Content"
        html = "<div id='article_3' class='newest urgent'>Content</div>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)
        
    def test_inline_variables_are_parsed_correctly(self):
        haml = "%h1 Hello, #{name}, how are you?"
        html = "<h1>Hello, {{ name }}, how are you?</h1>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)
        
    def test_inline_variables_are_parsed_correctly_web2py(self):
        haml = "%h1 Hello, #{name}, how are you?"
        html = "<h1>Hello, {{ =name }}, how are you?</h1>\n"
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_with_special_characters_are_parsed_correctly(self):
        haml = "%h1 Hello, #{person.name}, how are you?"
        html = "<h1>Hello, {{ person.name }}, how are you?</h1>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)
        
    def test_inline_variables_with_special_characters_are_parsed_correctly_web2py(self):
        haml = "%h1 Hello, #{person.name}, how are you?"
        html = "<h1>Hello, {{ =person.name }}, how are you?</h1>\n"
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result)
        
    def test_inline_fncall_parsed_correctly_web2py(self):
        haml = "%h1 Hello, #{person.get_name()}, how are you?"
        html = "<h1>Hello, {{ =person.get_name() }}, how are you?</h1>\n"
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result)   
    
    def test_tag_attr_inline_fncall_parsed_correctly_web2py(self):
        haml = "%h1 Hello, #{person.get_name()}, how are you?"
        html = "<h1>Hello, {{ =person.get_name() }}, how are you?</h1>\n"
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result)    
    
        
    def test_web2py_assignment(self):
        haml = "- test = 'test'"
        html = "{{ test = 'test' }}"
        hamlParser = hamlpy.Compiler('web2py')
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))
        
        
        
if __name__ == '__main__':
    unittest.main()