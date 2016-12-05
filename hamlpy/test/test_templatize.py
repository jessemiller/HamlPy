from __future__ import unicode_literals

import unittest

from django.template.base import Origin
from django.utils.translation import templatize as real_templatize


class TemplatizeTest(unittest.TestCase):

    def test_templatize(self):
        # test regular Django tags
        self.assertEqual(
            real_templatize('{% trans "Foo" %}{% blocktrans %}\nBar\n{% endblocktrans %}', Origin('test.html')),
            " gettext(u'Foo')  gettext(u'\\nBar\\n') \nSSS\n"
        )

        # test Haml tags with HTML origin
        self.assertEqual(
            real_templatize('- trans "Foo"\n- blocktrans\n  Bar\n', Origin('test.haml')),
            " gettext(u'Foo') \n gettext(u'\\n  Bar\\n\\n') \n  SSS\n\n\n"
        )

        # test Haml tags and HTML origin
        self.assertEqual(
            real_templatize('- trans "Foo"\n- blocktrans\n  Bar\n', Origin('test.html')),
            "X XXXXX XXXXX\nX XXXXXXXXXX\n  XXX\n"
        )

        # test Haml tags and no origin
        self.assertEqual(
            real_templatize('- trans "Foo"\n- blocktrans\n  Bar\n'),
            "X XXXXX XXXXX\nX XXXXXXXXXX\n  XXX\n"
        )
