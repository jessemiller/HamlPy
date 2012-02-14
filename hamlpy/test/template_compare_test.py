import codecs
import unittest
from nose.tools import eq_
from hamlpy import hamlpy

class TestTemplateCompare(unittest.TestCase):

    def test_comparing_simple_templates(self):
        self._compare_test_files('simple')
        
    def test_mixed_id_and_classes_using_dictionary(self):
        self._compare_test_files('classIdMixtures')
    
    def test_self_closing_tags_close(self):
        self._compare_test_files('selfClosingTags')
        
    def test_nested_html_comments(self):
        self._compare_test_files('nestedComments')
        
    def test_haml_comments(self):
        self._compare_test_files('hamlComments')
        
    def test_implicit_divs(self):
        self._compare_test_files('implicitDivs')
        
    def test_django_combination_of_tags(self):
        self._compare_test_files('djangoCombo')
        
    def test_self_closing_django(self):
        self._compare_test_files('selfClosingDjango')
        
    def test_nested_django_tags(self):
        self._compare_test_files('nestedDjangoTags')
        
    def test_filters(self):
        self._compare_test_files('filters')
    
    def test_nested_if_else_blocks(self):
        self._compare_test_files('nestedIfElseBlocks')

    def test_all_if_types(self):
        self._compare_test_files('allIfTypesTest')

    def test_multi_line_dict(self):
        self._compare_test_files('multiLineDict')

    def test_filter_multiline_ignore(self):
        self._compare_test_files('filterMultilineIgnore')

    def _find_diff(self, s1, s2):
        if len(s1)>len(s2):
            shorter=s2
        else:
            shorter=s1

        line=1
        col=1
        
        for i, _ in enumerate(shorter):
            if shorter[i]=='\n':
                line += 1
                col=1
            if s1[i] != s2[i]:
                return line,col,s1[i],s2[i]

            col+=1

        return -1,-1,'',''

    def _compare_test_files(self, name):
        haml_lines = codecs.open('templates/'+name+'.hamlpy', encoding='utf-8').readlines()
        html = open('templates/'+name+'.html').read()
        
        haml_compiler = hamlpy.Compiler()
        parsed = haml_compiler.process_lines(haml_lines)

        # Ignore line ending differences
        parsed=parsed.replace('\r','')
        html=html.replace('\r','')
        
        line,col,c1,c2 = self._find_diff(parsed, html)
        if line != -1:
            print 'HAML generated: '
            print parsed
            print 'Difference begins at line', line, 'column', col
            print 'Character code in parsed:', ord(c1)
            print 'Character code in HTML file:', ord(c2)
        eq_(parsed, html)
        
if __name__ == '__main__':
    unittest.main()
