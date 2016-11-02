from __future__ import print_function, unicode_literals

import unittest

from hamlpy import nodes
from hamlpy import hamlpy


class ElementNodeTest(unittest.TestCase):
    def test_calculates_indentation_properly(self):
        no_indentation = nodes.ElementNode('%div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual(0, no_indentation.indentation)
        
        three_indentation = nodes.ElementNode('   %div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual(3, three_indentation.indentation)
        
        six_indentation = nodes.ElementNode('      %div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual(6, six_indentation.indentation)

    def test_indents_tabs_properly(self):
        no_indentation = nodes.ElementNode('%div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual('', no_indentation.spaces)

        one_tab = nodes.HamlNode('	%div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual('\t', one_tab.spaces)

        one_space = nodes.HamlNode(' %div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual(' ', one_space.spaces)

        three_tabs = nodes.HamlNode('			%div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual('\t\t\t', three_tabs.spaces)

        tab_space = nodes.HamlNode('	 %div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual('\t\t', tab_space.spaces)

        space_tab = nodes.HamlNode(' 	%div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual('  ', space_tab.spaces)

    def test_lines_are_always_stripped_of_whitespace(self):
        some_space = nodes.ElementNode('   %div', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual('%div', some_space.haml)
        
        lots_of_space = nodes.ElementNode('      %div    ', hamlpy.DEFAULT_OPTIONS)
        self.assertEqual('%div', lots_of_space.haml)
    
    def test_inserts_nodes_into_proper_tree_depth(self):
        no_indentation_node = nodes.ElementNode('%div', hamlpy.DEFAULT_OPTIONS)
        one_indentation_node = nodes.ElementNode(' %div', hamlpy.DEFAULT_OPTIONS)
        two_indentation_node = nodes.ElementNode('  %div', hamlpy.DEFAULT_OPTIONS)
        another_one_indentation_node = nodes.ElementNode(' %div', hamlpy.DEFAULT_OPTIONS)
        
        no_indentation_node.add_node(one_indentation_node)
        no_indentation_node.add_node(two_indentation_node)
        no_indentation_node.add_node(another_one_indentation_node)
        
        self.assertEqual(one_indentation_node, no_indentation_node.children[0])
        self.assertEqual(two_indentation_node, no_indentation_node.children[0].children[0])
        self.assertEqual(another_one_indentation_node, no_indentation_node.children[1])
    
    def test_adds_multiple_nodes_to_one(self):
        start = nodes.ElementNode('%div', hamlpy.DEFAULT_OPTIONS)
        one = nodes.ElementNode('  %div', hamlpy.DEFAULT_OPTIONS)
        two = nodes.ElementNode('  %div', hamlpy.DEFAULT_OPTIONS)
        three = nodes.ElementNode('  %div', hamlpy.DEFAULT_OPTIONS)
        
        start.add_node(one)
        start.add_node(two)
        start.add_node(three)
        
        self.assertEqual(3, len(start.children))

    def test_node_parent_function(self):
        root = nodes.ElementNode('%div.a', hamlpy.DEFAULT_OPTIONS)
        elements = [
            {'node': nodes.ElementNode('  %div.b', hamlpy.DEFAULT_OPTIONS), 'expected_parent': 'root'},
            {'node': nodes.ElementNode('  %div.c', hamlpy.DEFAULT_OPTIONS), 'expected_parent': 'root'},
            {'node': nodes.ElementNode('    %div.d', hamlpy.DEFAULT_OPTIONS), 'expected_parent': 'elements[1]["node"]'},
            {'node': nodes.ElementNode('      %div.e', hamlpy.DEFAULT_OPTIONS), 'expected_parent': 'elements[2]["node"]'},
            {'node': nodes.ElementNode('  %div.f', hamlpy.DEFAULT_OPTIONS), 'expected_parent': 'root'},
        ]

        for el in elements:
            self.assertEqual(root.parent_of(el['node']), eval(el['expected_parent']))
            root.add_node(el['node'])
