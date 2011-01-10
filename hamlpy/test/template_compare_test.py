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
        
    def test_web2py_combination_of_tags(self):
        self._compare_test_files('web2pyCombo', 'web2py')
        
    def test_self_closing_web2py(self):
        self._compare_test_files('selfClosingWeb2py', 'web2py')
        
    def test_nested_web2py_tags(self):
        self._compare_test_files('nestedWeb2pyTags', 'web2py')
        
    def test_filters(self):
        self._compare_test_files('filters')
        
    def _compare_test_files(self, name, template_type='django'):
        haml_lines = codecs.open('templates/'+name+'.hamlpy', encoding='utf-8').readlines()
        html = open('templates/'+name+'.html').read()
        
        haml_compiler = hamlpy.Compiler(template_type)
        parsed = haml_compiler.process_lines(haml_lines)
            
        eq_(parsed, html)
        
if __name__ == '__main__':
    unittest.main()