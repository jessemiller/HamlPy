# -*- coding: utf-8 -*-
import unittest
from nose.tools import eq_, raises
from hamlpy import hamlpy

class RegressionTest(unittest.TestCase):
    # Regression test for Github Issue 92
    def test_haml_comment_nodes_dont_post_render_children(self):
        haml = '''
        -# My comment
            #my_div
                my text
        test
        '''
        html = "test"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.strip())
        
    def test_whitespace_after_attribute_key(self):
        haml = '%form{id : "myform"}'
        html = "<form id='myform'></form>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.strip())
    
    def test_for_newline_after_conditional_comment(self):
        haml = '/[if lte IE 7]\n\ttest\n#test'
        haml = '<!--[if lte IE 7]>\n\ttest\n<![endif]-->\n<div id="test"></div>'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result.strip())
