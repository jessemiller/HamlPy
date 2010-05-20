import unittest
from hamlpy import hamlpy

class TestElementNode(unittest.TestCase):
    
    def testCalculatesIndentationProperly(self):
        noIndentation = hamlpy.ElementNode('%div')
        self.assertEqual(0, noIndentation.indentation)
        
        threeIndentation = hamlpy.ElementNode('   %div')
        self.assertEqual(3, threeIndentation.indentation)
        
        sixIndentation = hamlpy.ElementNode('      %div')
        self.assertEqual(6, sixIndentation.indentation)
        
    def testLinesAreAlwaysStrippedOfWhiteSpace(self):
        someSpace = hamlpy.ElementNode('   %div')
        self.assertEqual('%div', someSpace.haml)
        
        lotsOfSpace = hamlpy.ElementNode('      %div    ')
        self.assertEqual('%div', lotsOfSpace.haml)
        
    def testInsertsNodesIntoProperTreeDepth(self):
        noIndentationNode = hamlpy.ElementNode('%div')
        oneIndentationNode = hamlpy.ElementNode(' %div')
        twoIndentationNode = hamlpy.ElementNode('  %div')
        anotherOneIndentation = hamlpy.ElementNode(' %div')
        
        noIndentationNode.addNode(oneIndentationNode)
        noIndentationNode.addNode(twoIndentationNode)
        noIndentationNode.addNode(anotherOneIndentation)
        
        self.assertEqual(oneIndentationNode, noIndentationNode.internalNodes[0])
        self.assertEqual(twoIndentationNode, noIndentationNode.internalNodes[0].internalNodes[0])
        self.assertEqual(anotherOneIndentation, noIndentationNode.internalNodes[1])

    def test_adds_multiple_nodes_to_one(self):
        startNode = hamlpy.ElementNode('%div')
        oneNode = hamlpy.ElementNode('  %div')
        twoNode = hamlpy.ElementNode('  %div')
        threeNode = hamlpy.ElementNode('  %div')
        
        startNode.addNode(oneNode)
        startNode.addNode(twoNode)
        startNode.addNode(threeNode)
        
        self.assertEqual(3, len(startNode.internalNodes))