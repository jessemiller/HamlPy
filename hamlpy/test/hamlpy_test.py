# -*- coding: utf-8 -*-
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

    def test_dictionaries_can_by_pythonic(self):
        haml = "%div{'id':['Article','1'], 'class':['article','entry','visible']} Booyaka"
        html = "<div id='Article_1' class='article entry visible'>Booyaka</div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result.replace('\n', ''))


    def test_html_comments_rendered_properly(self):
        haml = '/ some comment'
        html = "<!-- some comment -->"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))

    def test_conditional_comments_rendered_properly(self):
        haml = "/[if IE]\n  %h1 You use a shitty browser"
        html = "<!--[if IE]>\n  <h1>You use a shitty browser</h1>\n<![endif]-->\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_single_line_conditional_comments_rendered_properly(self):
        haml = "/[if IE] You use a shitty browser"
        html = "<!--[if IE]> You use a shitty browser<![endif]-->\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_django_variables_on_tag_render_properly(self):
        haml = '%div= story.tease'
        html = '<div>{{ story.tease }}</div>'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))

    def test_stand_alone_django_variables_render(self):
        haml = '= story.tease'
        html = '{{ story.tease }}'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))

    def test_stand_alone_django_tags_render(self):
        haml = '- extends "something.html"'
        html = '{% extends "something.html" %}'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))

    def test_if_else_django_tags_render(self):
        haml = '- if something\n   %p hello\n- else\n   %p goodbye'
        html = '{% if something %}\n   <p>hello</p>\n{% else %}\n   <p>goodbye</p>\n{% endif %}\n'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    @raises(TypeError)
    def test_throws_exception_when_trying_to_close_django(self):
        haml = '- endfor'
        hamlParser = hamlpy.Compiler()
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
        haml = "={greeting} #{name}, how are you ={date}?"
        html = "{{ greeting }} {{ name }}, how are you {{ date }}?\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_can_use_filter_characters(self):
        haml = "={value|center:\"15\"}"
        html = "{{ value|center:\"15\" }}\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_in_attributes_are_parsed_correctly(self):
        haml = "%a{'b': '={greeting} test'} blah"
        html = "<a b='{{ greeting }} test'>blah</a>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_in_attributes_work_in_id(self):
        haml = "%div{'id':'package_={object.id}'}"
        html = "<div id='package_{{ object.id }}'></div>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_in_attributes_work_in_class(self):
        haml = "%div{'class':'package_={object.id}'}"
        html = "<div class='package_{{ object.id }}'></div>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_in_attributes_are_escaped_correctly(self):
        haml = "%a{'b': '\\\\={greeting} test', title: \"It can't be removed\"} blah"
        html = "<a b='={greeting} test' title='It can\\'t be removed'>blah</a>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_escaping_works(self):
        haml = "%h1 Hello, \\#{name}, how are you ={ date }?"
        html = "<h1>Hello, #{name}, how are you {{ date }}?</h1>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_escaping_works_at_start_of_line(self):
        haml = "\\={name}, how are you?"
        html = "={name}, how are you?\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_with_hash_escaping_works_at_start_of_line(self):
        haml = "\\#{name}, how are you?"
        html = "#{name}, how are you?\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_work_at_start_of_line(self):
        haml = "={name}, how are you?"
        html = "{{ name }}, how are you?\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_with_hash_work_at_start_of_line(self):
        haml = "#{name}, how are you?"
        html = "{{ name }}, how are you?\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_inline_variables_with_special_characters_are_parsed_correctly(self):
        haml = "%h1 Hello, #{person.name}, how are you?"
        html = "<h1>Hello, {{ person.name }}, how are you?</h1>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_plain_text(self):
        haml = "This should be plain text\n    This should be indented"
        html = "This should be plain text\n    This should be indented\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_plain_text_with_indenting(self):
        haml = "This should be plain text"
        html = "This should be plain text\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_escaped_haml(self):
        haml = "\\= Escaped"
        html = "= Escaped\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_utf8_with_regular_text(self):
        haml = u"%a{'href':'', 'title':'링크(Korean)'} Some Link"
        html = u"<a href='' title='\ub9c1\ud06c(Korean)'>Some Link</a>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_python_filter(self):
        haml = ":python\n   for i in range(0, 5): print \"<p>item \%s</p>\" % i"
        html = '<p>item \\0</p>\n<p>item \\1</p>\n<p>item \\2</p>\n<p>item \\3</p>\n<p>item \\4</p>\n'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_doctype_html5(self):
        haml = '!!! 5'
        html = '<!DOCTYPE html>'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))

    def test_doctype_xhtml(self):
        haml = '!!!'
        html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))

    def test_doctype_xml_utf8(self):
        haml = '!!! XML'
        html = "<?xml version='1.0' encoding='utf-8' ?>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))

    def test_doctype_xml_encoding(self):
        haml = '!!! XML iso-8859-1'
        html = "<?xml version='1.0' encoding='iso-8859-1' ?>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.replace('\n', ''))

    def test_plain_filter_with_indentation(self):
        haml = ":plain\n    -This should be plain text\n    .This should be more\n      This should be indented"
        html = "-This should be plain text\n.This should be more\n  This should be indented\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_plain_filter_with_no_children(self):
        haml = ":plain\nNothing"
        html = "Nothing\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_filters_render_escaped_backslash(self):
        haml = ":plain\n  \\Something"
        html = "\\Something\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_xml_namespaces(self):
        haml = "%fb:tag\n  content"
        html = "<fb:tag>\n  content\n</fb:tag>\n"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_pygments_filter(self):
        haml = '''
            :highlight
              print "hi"

              if x:
                  print "y":
              else:
                  print "z":
        '''
        html = '\n<div class="highlight"><pre><span class="n">print</span> &quot;<span class="n">hi</span>&quot;' \
                + '\n\n<span class="k">if</span> <span class="n">x</span><span class="p">:</span>' \
                + '\n    <span class="n">print</span> &quot;<span class="n">y</span>&quot;<span class="p">:</span>' \
                + '\n<span class="k">else</span><span class="p">:</span>' \
                + '\n    <span class="n">print</span> &quot;<span class="n">z</span>&quot;<span class="p">:</span>' \
                + '\n</pre></div>\n'

        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)

    def test_attr_wrapper(self):
        haml = """
%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}
  %body#main
    %div.wrap
      %a{:href => '/'}
:javascript"""
        hamlParser = hamlpy.Compiler(options_dict={'attr_wrapper': '"'})
        result = hamlParser.process(haml)
        self.assertEqual(result,
                         '''<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <body id="main">
    <div class="wrap">
      <a href="/"></a>
    </div>
  </body>
</html>
<script type="text/javascript">
// <![CDATA[
// ]]>
</script>
''')

if __name__ == '__main__':
    unittest.main()
