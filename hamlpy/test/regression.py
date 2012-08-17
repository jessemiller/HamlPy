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
        