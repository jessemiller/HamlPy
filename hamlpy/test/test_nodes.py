from __future__ import print_function, unicode_literals

import unittest

from hamlpy import hamlpy
from hamlpy.parser import nodes


class NodesTest(unittest.TestCase):

    def test_node_factory(self):
        assert isinstance(self._create_node('%div'), nodes.ElementNode)
        assert isinstance(self._create_node('   %html'), nodes.ElementNode)
        assert isinstance(self._create_node('.className'), nodes.ElementNode)
        assert isinstance(self._create_node('   .className'), nodes.ElementNode)
        assert isinstance(self._create_node('#idName'), nodes.ElementNode)
        assert isinstance(self._create_node('   #idName'), nodes.ElementNode)
        assert isinstance(self._create_node('/ some Comment'), nodes.CommentNode)
        assert isinstance(self._create_node('     / some Comment'), nodes.CommentNode)
        assert isinstance(self._create_node('just some random text'), nodes.HamlNode)
        assert isinstance(self._create_node('   more random text'), nodes.HamlNode)
        assert isinstance(self._create_node('-# This is a haml comment'), nodes.HamlCommentNode)
        assert isinstance(self._create_node('= some.variable'), nodes.VariableNode)
        assert isinstance(self._create_node('- for something in somethings'), nodes.TagNode)
        assert isinstance(self._create_node('\\= some.variable'), nodes.HamlNode)
        assert isinstance(self._create_node('    \\= some.variable'), nodes.HamlNode)
        assert isinstance(self._create_node(':python'), nodes.PythonFilterNode)
        assert isinstance(self._create_node('/[if IE 5]'), nodes.ConditionalCommentNode)

    @staticmethod
    def _create_node(line):
        return nodes.create_node(line, hamlpy.DEFAULT_OPTIONS)
