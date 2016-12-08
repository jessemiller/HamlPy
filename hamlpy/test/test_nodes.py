from __future__ import absolute_import, print_function, unicode_literals

import unittest

from hamlpy.compiler import Compiler
from hamlpy.parser import nodes
from hamlpy.parser.generic import Stream
from hamlpy.parser.nodes import read_node, read_filter_node


class NodeTest(unittest.TestCase):

    def test_read_node(self):
        assert isinstance(self._read_node('%div'), nodes.ElementNode)
        assert isinstance(self._read_node('   %html'), nodes.ElementNode)
        assert isinstance(self._read_node('.className'), nodes.ElementNode)
        assert isinstance(self._read_node('   .className'), nodes.ElementNode)
        assert isinstance(self._read_node('#idName'), nodes.ElementNode)
        assert isinstance(self._read_node('   #idName'), nodes.ElementNode)
        assert isinstance(self._read_node('/ some Comment'), nodes.CommentNode)
        assert isinstance(self._read_node('     / some Comment'), nodes.CommentNode)
        assert isinstance(self._read_node('just some random text'), nodes.PlaintextNode)
        assert isinstance(self._read_node('   more random text'), nodes.PlaintextNode)
        assert isinstance(self._read_node('-# This is a haml comment'), nodes.HamlCommentNode)
        assert isinstance(self._read_node('= some.variable'), nodes.VariableNode)
        assert isinstance(self._read_node('- for something in somethings'), nodes.TagNode)
        assert isinstance(self._read_node('\\= some.variable'), nodes.PlaintextNode)
        assert isinstance(self._read_node('    \\= some.variable'), nodes.PlaintextNode)
        assert isinstance(self._read_node('/[if IE 5]'), nodes.ConditionalCommentNode)
        assert isinstance(self._read_node(':plain'), nodes.FilterNode)
        assert isinstance(self._read_node('   :css\n'), nodes.FilterNode)
        assert isinstance(self._read_node(':stylus'), nodes.FilterNode)
        assert isinstance(self._read_node(':javascript'), nodes.FilterNode)
        assert isinstance(self._read_node(':coffee'), nodes.FilterNode)

    def test_read_filter_node(self):
        stream = Stream(':python\n  print("hello")\n')
        node = read_filter_node(stream, '', Compiler())
        assert node.filter_name == 'python'
        assert node.content == '  print("hello")'
        assert stream.text[stream.ptr:] == ''

        stream = Stream(':javascript\n    var i = 0;\n  var j = 1;\n%span')
        node = read_filter_node(stream, '', Compiler())
        assert node.filter_name == 'javascript'
        assert node.content == '    var i = 0;\n  var j = 1;'
        assert stream.text[stream.ptr:] == '%span'

    def test_calculates_indentation_properly(self):
        no_indentation = self._read_node('%div')
        self.assertEqual(0, no_indentation.indentation)

        three_indentation = self._read_node('   %div')
        self.assertEqual(3, three_indentation.indentation)

        six_indentation = self._read_node('      %div')
        self.assertEqual(6, six_indentation.indentation)

    def test_indents_tabs_properly(self):
        no_indentation = self._read_node('%div')
        self.assertEqual('', no_indentation.indent)

        one_tab = self._read_node('	%div')
        self.assertEqual('\t', one_tab.indent)

        one_space = self._read_node(' %div')
        self.assertEqual(' ', one_space.indent)

        three_tabs = self._read_node('			%div')
        self.assertEqual('\t\t\t', three_tabs.indent)

        tab_space = self._read_node('	 %div')
        self.assertEqual('\t\t', tab_space.indent)

        space_tab = self._read_node(' 	%div')
        self.assertEqual('  ', space_tab.indent)

    def test_lines_are_always_stripped_of_whitespace(self):
        some_space = self._read_node('   text')
        self.assertEqual('text', some_space.haml)

        lots_of_space = self._read_node('      text    ')
        self.assertEqual('text', lots_of_space.haml)

    def test_inserts_nodes_into_proper_tree_depth(self):
        no_indentation_node = self._read_node('%div')
        one_indentation_node = self._read_node(' %div')
        two_indentation_node = self._read_node('  %div')
        another_one_indentation_node = self._read_node(' %div')

        no_indentation_node.add_node(one_indentation_node)
        no_indentation_node.add_node(two_indentation_node)
        no_indentation_node.add_node(another_one_indentation_node)

        self.assertEqual(one_indentation_node, no_indentation_node.children[0])
        self.assertEqual(two_indentation_node, no_indentation_node.children[0].children[0])
        self.assertEqual(another_one_indentation_node, no_indentation_node.children[1])

    def test_adds_multiple_nodes_to_one(self):
        start = self._read_node('%div')
        one = self._read_node('  %div')
        two = self._read_node('  %div')
        three = self._read_node('  %div')

        start.add_node(one)
        start.add_node(two)
        start.add_node(three)

        self.assertEqual(3, len(start.children))

    @staticmethod
    def _read_node(haml):
        return read_node(Stream(haml), None, Compiler())
