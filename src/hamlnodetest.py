import unittest
import hamlpy

class HamlNodeTest(unittest.TestCase):
    
    def testCalculatesIndentationProperly(self):
        noIndentation = hamlpy.HamlNode('%div')
        self.assertEqual(0, noIndentation.indentation)
        
        threeIndentation = hamlpy.HamlNode('   %div')
        self.assertEqual(3, threeIndentation.indentation)
        
        sixIndentation = hamlpy.HamlNode('      %div')
        self.assertEqual(6, sixIndentation.indentation)
        
    def testLinesAreAlwaysStrippedOfWhiteSpace(self):
        someSpace = hamlpy.HamlNode('   %div')
        self.assertEqual('%div', someSpace.haml)
        
        lotsOfSpace = hamlpy.HamlNode('      %div    ')
        self.assertEqual('%div', lotsOfSpace.haml)
        
    def testInsertsNodesIntoProperTreeDepth(self):
        noIndentationNode = hamlpy.HamlNode('%div')
        oneIndentationNode = hamlpy.HamlNode(' %div')
        twoIndentationNode = hamlpy.HamlNode('  %div')
        anotherOneIndentation = hamlpy.HamlNode(' %div')
        
        noIndentationNode.addNode(oneIndentationNode)
        noIndentationNode.addNode(twoIndentationNode)
        noIndentationNode.addNode(anotherOneIndentation)
        
        self.assertEqual(oneIndentationNode, noIndentationNode.internalNodes[0])
        self.assertEqual(twoIndentationNode, noIndentationNode.internalNodes[0].internalNodes[0])
        self.assertEqual(anotherOneIndentation, noIndentationNode.internalNodes[1])
