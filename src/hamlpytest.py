import unittest
import hamlpy

class HamlPyTest(unittest.TestCase):
    htmlValues = ( ('<h1></h1>', '%h1'),
                   ('<div></div>', '%div'))
    
    def testOutputsSimpleHtmlProperly(self):
        hamlParser = hamlpy.Compiler()
        for html, haml in self.htmlValues:
            result = hamlParser.process(haml)
            self.assertEqual(html, result)
            
    def testFillsInElementsOnSingleLine(self):
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process('%div Some Text')
        self.assertEqual('<div>Some Text</div>', result)
        
    def testMultipleLinesOfSimpleHamlWork(self):
        haml = '%div Some Text\n%h1 More Text'
        html = '<div>Some Text</div><h1>More Text</h1>'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result)
        
    def testIndentedLinesNestElements(self):
        haml = '%div\n   %h1 More Text'
        html = '<div><h1>More Text</h1></div>'
        hamlParser = hamlpy.Compiler()
        result = hamlParser.process(haml)
        self.assertEqual(html, result)
        
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