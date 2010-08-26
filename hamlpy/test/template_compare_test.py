import codecs
from nose.tools import eq_
from hamlpy import hamlpy

class TestTemplateCompare():
    
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
        
    def _compare_test_files(self, name):
        haml_lines = codecs.open('templates/'+name+'.hamlpy', encoding='utf-8').readlines()
        html = open('templates/'+name+'.html').read()
        
        haml_compiler = hamlpy.Compiler()
        parsed = haml_compiler.process_lines(haml_lines)
        eq_(parsed, html)
        
