from __future__ import absolute_import, print_function, unicode_literals

import unittest

from hamlpy.hamlpy import Compiler
from hamlpy.parser import nodes


class ElementNodeTest(unittest.TestCase):
    def test_calculates_indentation_properly(self):
        no_indentation = self._create_node('%div')
        self.assertEqual(0, no_indentation.indentation)

        three_indentation = self._create_node('   %div')
        self.assertEqual(3, three_indentation.indentation)

        six_indentation = self._create_node('      %div')
        self.assertEqual(6, six_indentation.indentation)

    def test_indents_tabs_properly(self):
        no_indentation = self._create_node('%div')
        self.assertEqual('', no_indentation.spaces)

        one_tab = self._create_node('	%div')
        self.assertEqual('\t', one_tab.spaces)

        one_space = self._create_node(' %div')
        self.assertEqual(' ', one_space.spaces)

        three_tabs = self._create_node('			%div')
        self.assertEqual('\t\t\t', three_tabs.spaces)

        tab_space = self._create_node('	 %div')
        self.assertEqual('\t\t', tab_space.spaces)

        space_tab = self._create_node(' 	%div')
        self.assertEqual('  ', space_tab.spaces)

    def test_lines_are_always_stripped_of_whitespace(self):
        some_space = self._create_node('   %div')
        self.assertEqual('%div', some_space.haml)

        lots_of_space = self._create_node('      %div    ')
        self.assertEqual('%div', lots_of_space.haml)

    def test_inserts_nodes_into_proper_tree_depth(self):
        no_indentation_node = self._create_node('%div')
        one_indentation_node = self._create_node(' %div')
        two_indentation_node = self._create_node('  %div')
        another_one_indentation_node = self._create_node(' %div')

        no_indentation_node.add_node(one_indentation_node)
        no_indentation_node.add_node(two_indentation_node)
        no_indentation_node.add_node(another_one_indentation_node)

        self.assertEqual(one_indentation_node, no_indentation_node.children[0])
        self.assertEqual(two_indentation_node, no_indentation_node.children[0].children[0])
        self.assertEqual(another_one_indentation_node, no_indentation_node.children[1])

    def test_adds_multiple_nodes_to_one(self):
        start = self._create_node('%div')
        one = self._create_node('  %div')
        two = self._create_node('  %div')
        three = self._create_node('  %div')

        start.add_node(one)
        start.add_node(two)
        start.add_node(three)

        self.assertEqual(3, len(start.children))

    def test_node_parent_function(self):
        root = self._create_node('%div.a')
        elements = [
            {'node': self._create_node('  %div.b'), 'expected_parent': 'root'},
            {'node': self._create_node('  %div.c'), 'expected_parent': 'root'},
            {'node': self._create_node('    %div.d'), 'expected_parent': 'elements[1]["node"]'},
            {'node': self._create_node('      %div.e'), 'expected_parent': 'elements[2]["node"]'},
            {'node': self._create_node('  %div.f'), 'expected_parent': 'root'},
        ]

        for el in elements:
            self.assertEqual(root.parent_of(el['node']), eval(el['expected_parent']))
            root.add_node(el['node'])

    def _create_node(self, haml):
        return nodes.ElementNode(haml, Compiler())
