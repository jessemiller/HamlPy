from django.test import SimpleTestCase


class TemplatizeTest(SimpleTestCase):

    def test_templatize(self):
        from django.utils.translation import templatize

        # test regular Django tags
        output = templatize('{% trans "Foo" %}{% blocktrans %}\nBar\n{% endblocktrans %}', origin='test.html')
        self.assertRegex(output, r"gettext\(u?'Foo'\)")
        self.assertRegex(output, r"gettext\(u?'\\nBar\\n'\)")

        # test Haml tags with HTML origin
        output = templatize('- trans "Foo"\n- blocktrans\n  Bar\n', origin='test.haml')
        self.assertRegex(output, r"gettext\(u?'Foo'\)")
        self.assertRegex(output, r"gettext\(u?'\\n  Bar\\n'\)")

        # test Haml tags and HTML origin
        self.assertNotIn('gettext', templatize('- trans "Foo"\n- blocktrans\n  Bar\n', origin='test.html'))

        # test Haml tags and no origin
        self.assertNotIn('gettext', templatize('- trans "Foo"\n- blocktrans\n  Bar\n'))
