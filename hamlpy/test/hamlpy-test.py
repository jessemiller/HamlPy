import unittest
from nose.tools import eq_
from hamlpy import hamlpy

class HamlPyTest(unittest.TestCase):
    htmlValues = ( ('<h1></h1>', '%h1'),
                   ('<div></div>', '%div'),
                   ('<one><two><three>Hey there</three></two></one>', '%one\n  %two\n    %three Hey there'),
                   ('<gee><whiz>Wow this is cool!</whiz></gee>', '%gee\n  %whiz\n    Wow this is cool!'))
    
    def testOutputsSimpleHtmlProperly(self):
        hamlParser = hamlpy.Compiler()
        for html, haml in self.htmlValues:
            result = hamlParser.process(haml)
            assert html == result
        
    def testAppliesIdProperly(self):
        haml = '%div#someId Some text'
        html = "<div id='someId'>Some text</div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result)
        
    def testAppliesClassProperly(self):
        haml = '%div.someClass Some text'
        html = "<div class='someClass'>Some text</div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result)
        
    def testAppliesMultipleClassesProperly(self):
        haml = '%div.someClass.anotherClass Some text'
        html = "<div class='someClass anotherClass'>Some text</div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result)

    def testDictionariesDefineAttributes(self):
        haml = "%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertTrue("<html" in result)
        self.assertTrue("xmlns='http://www.w3.org/1999/xhtml'" in result)
        self.assertTrue("xml:lang='en'" in result)
        self.assertTrue("lang='en'" in result)
        self.assertTrue(result.endswith("></html>"))
    
    def testDictionariesSupportArraysForId(self):
        haml = "%div{'id':('itemType', '5')}"
        html = "<div id='itemType_5'></div>"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result)
        
    def test_html_comments_rendered_properly(self):
        haml = '/ some comment'
        html = "<!-- some comment -->"
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        eq_(html, result)