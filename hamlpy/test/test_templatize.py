from __future__ import unicode_literals

import unittest

from django.template.base import Origin
from django.utils.translation import templatize as real_templatize


class TemplatizeTest(unittest.TestCase):

    def test_templatize(self):
        # test regular Django tags
        output = real_templatize('{% trans "Foo" %}{% blocktrans %}\nBar\n{% endblocktrans %}', Origin('test.html'))
        self.assertRegexpMatches(output, r"gettext\(u?'Foo'\)")
        self.assertRegexpMatches(output, r"gettext\(u?'\\nBar\\n'\)")

        # test Haml tags with HTML origin
        output = real_templatize('- trans "Foo"\n- blocktrans\n  Bar\n', Origin('test.haml'))
        self.assertRegexpMatches(output, r"gettext\(u?'Foo'\)")
        self.assertRegexpMatches(output, r"gettext\(u?'\\n  Bar\\n'\)")

        # test Haml tags and HTML origin
        self.assertNotIn('gettext', real_templatize('- trans "Foo"\n- blocktrans\n  Bar\n', Origin('test.html')))

        # test Haml tags and no origin
        self.assertNotIn('gettext', real_templatize('- trans "Foo"\n- blocktrans\n  Bar\n'))
