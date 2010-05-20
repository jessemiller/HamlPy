import codecs
from nose.tools import eq_
from hamlpy import hamlpy

class TestTemplateCompare():
    
    def test_comparing_simple_templates(self):
        self.__openAndReadAndTestFiles('simple')
        
    def test_mixed_id_and_classes_using_dictionary(self):
        self.__openAndReadAndTestFiles('classIdMixtures')
    
    def test_self_closing_tags_close(self):
        self.__openAndReadAndTestFiles('selfClosingTags')
        
    def test_nested_html_comments(self):
        self.__openAndReadAndTestFiles('nestedComments')
        
    def test_haml_comments(self):
        self.__openAndReadAndTestFiles('hamlComments')
        
    def test_implicit_divs(self):
        self.__openAndReadAndTestFiles('implicitDivs')
        
    def __openAndReadAndTestFiles(self, name):
        hamlLines = codecs.open('templates/'+name+'.hamlpy', encoding='utf-8').readlines()
        html = open('templates/'+name+'.html').read()
        
        hamlCompiler = hamlpy.Compiler()
        parsed = hamlCompiler.processLines(hamlLines)
        eq_(parsed, html)
        