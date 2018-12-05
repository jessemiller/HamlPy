import unittest

from jinja2.exceptions import TemplateSyntaxError

from hamlpy.jinja import HamlPyExtension


class JinjaTest(unittest.TestCase):

    def test_preprocess(self):
        extension = HamlPyExtension(None)

        assert extension.preprocess('%span Hello', 'test.haml') == "<span>Hello</span>\n"
        assert extension.preprocess('%span Hello', 'test.hamlpy') == "<span>Hello</span>\n"
        assert extension.preprocess('%span Hello', '../templates/test.hamlpy') == "<span>Hello</span>\n"

        # non-Haml extension should be ignored
        assert extension.preprocess('%span Hello', 'test.txt') == "%span Hello"

        # exceptions converted to Jinja2 exceptions
        self.assertRaisesRegex(
            TemplateSyntaxError,
            r'Unterminated string \(expected "\). @ "%span{"}"',
            extension.preprocess,
            '%span{"}',
            'test.haml',
        )
