import unittest
from hamlpy import nodes

class TestElementNode(unittest.TestCase):
    
    def test_calculates_indentation_properly(self):
        no_indentation = nodes.ElementNode('%div')
        self.assertEqual(0, no_indentation.indentation)
        
        three_indentation = nodes.ElementNode('   %div')
        self.assertEqual(3, three_indentation.indentation)
        
        six_indentation = nodes.ElementNode('      %div')
        self.assertEqual(6, six_indentation.indentation)
    
    def test_lines_are_always_stripped_of_whitespace(self):
        some_space = nodes.ElementNode('   %div')
        self.assertEqual('%div', some_space.haml)
        
        lots_of_space = nodes.ElementNode('      %div    ')
        self.assertEqual('%div', lots_of_space.haml)
    
    def test_inserts_nodes_into_proper_tree_depth(self):
        no_indentation_node = nodes.ElementNode('%div')
        one_indentation_node = nodes.ElementNode(' %div')
        two_indentation_node = nodes.ElementNode('  %div')
        another_one_indentation_node = nodes.ElementNode(' %div')
        
        no_indentation_node.add_node(one_indentation_node)
        no_indentation_node.add_node(two_indentation_node)
        no_indentation_node.add_node(another_one_indentation_node)
        
        self.assertEqual(one_indentation_node, no_indentation_node.internal_nodes[0])
        self.assertEqual(two_indentation_node, no_indentation_node.internal_nodes[0].internal_nodes[0])
        self.assertEqual(another_one_indentation_node, no_indentation_node.internal_nodes[1])
    
    def test_adds_multiple_nodes_to_one(self):
        start = nodes.ElementNode('%div')
        one = nodes.ElementNode('  %div')
        two = nodes.ElementNode('  %div')
        three = nodes.ElementNode('  %div')
        
        start.add_node(one)
        start.add_node(two)
        start.add_node(three)
        
        self.assertEqual(3, len(start.internal_nodes))

    def test_html_indentation_vs_haml_indentation(self):
        pass

if __name__ == "__main__":
    unittest.main()
