from __future__ import print_function, unicode_literals

import unittest

from jinja2.exceptions import TemplateSyntaxError

from hamlpy.ext import HamlPyExtension


class JinjaTest(unittest.TestCase):

    def test_preprocess(self):
        extension = HamlPyExtension(None)

        self.assertEqual(extension.preprocess('%span Hello', 'test.haml'), "<span>Hello</span>\n")
        self.assertEqual(extension.preprocess('%span Hello', 'test.hamlpy'), "<span>Hello</span>\n")
        self.assertEqual(extension.preprocess('%span Hello', '../templates/test.hamlpy'), "<span>Hello</span>\n")

        # non-Haml extension should be ignored
        self.assertEqual(extension.preprocess('%span Hello', 'test.txt'), "%span Hello")

        # exceptions converted to Jinja2 exceptions
        self.assertRaisesRegexp(TemplateSyntaxError, 'Unterminated string \(expected "\). @ "{"}"',
                                extension.preprocess, '%span{"}', 'test.haml')
