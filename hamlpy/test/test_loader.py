from __future__ import print_function, unicode_literals

import django
import unittest
import mock

from distutils.version import StrictVersion
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from hamlpy.hamlpy import Compiler

TEMPLATE_DIR = 'hamlpy/test/templates'
TEMPLATE_LOADERS = [
    'hamlpy.template.loaders.HamlPyFilesystemLoader',
    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
]

if StrictVersion(django.get_version()) >= StrictVersion('1.8'):
    settings.configure(TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [TEMPLATE_DIR],
            'OPTIONS': {'loaders': TEMPLATE_LOADERS, 'debug': True}
        }
    ])
else:
    settings.configure(TEMPLATE_DIRS=[TEMPLATE_DIR], TEMPLATE_LOADERS=TEMPLATE_LOADERS, TEMPLATE_DEBUG=True)

django.setup()


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        patch_compiler_class = mock.patch('hamlpy.hamlpy.Compiler', wraps=Compiler)

        self.mock_compiler_class = patch_compiler_class.start()
        self.addCleanup(patch_compiler_class.stop)

    def _load_test_template(self, name):
        return open('hamlpy/test/templates/' + name, 'r').read()

    def test_template_rendering(self):
        assert render_to_string('simple.hamlpy') == self._load_test_template('simple.html') + "\n"

        context = {
            'section': {'title': "News", 'subtitle': "Technology"},
            'story_list': [{
                'headline': "Haml Helps",
                'tease': "Many HAML users...",
                'get_absolute_url': lambda: "http://example.com/stories/1/"
            }]
        }

        actual_html = render_to_string('djangoCombo.hamlpy', context)

        assert "<h2>Technology</h2>" in actual_html
        assert "HAML HELPS" in actual_html
        assert "<a href='http://example.com/stories/1/'>" in actual_html
        assert "<p>Many HAML users...</p>"

    def test_should_ignore_non_haml_templates(self):
        assert render_to_string('simple.html') == self._load_test_template('simple.html')

    def test_should_raise_exception_when_template_doesnt_exist(self):
        self.assertRaises(TemplateDoesNotExist, render_to_string, 'simple.xyz')
