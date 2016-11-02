from __future__ import print_function, unicode_literals

import django
import hamlpy
import mock
import unittest

from distutils.version import StrictVersion
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.test.utils import override_settings
from six.moves import reload_module

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


class LoaderTest(unittest.TestCase):
    def tearDown(self):
        reload_module(hamlpy.template.loaders)

    @mock.patch('hamlpy.hamlpy.Compiler', wraps=Compiler)
    def test_compiler_settings(self, mock_compiler_class):
        render_to_string('simple.hamlpy')

        mock_compiler_class.assert_called_once_with(options_dict={})
        mock_compiler_class.reset_mock()

        with override_settings(HAMLPY_ATTR_WRAPPER='"'):
            reload_module(hamlpy.template.loaders)

            rendered = render_to_string('simple.hamlpy')

            mock_compiler_class.assert_called_once_with(options_dict={'attr_wrapper': '"'})
            assert '"someClass"' in rendered

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

        rendered = render_to_string('djangoCombo.hamlpy', context)

        assert "<h2>Technology</h2>" in rendered
        assert "HAML HELPS" in rendered
        assert "<a href='http://example.com/stories/1/'>" in rendered
        assert "<p>Many HAML users...</p>"

    def test_should_ignore_non_haml_templates(self):
        assert render_to_string('simple.html') == self._load_test_template('simple.html')

    def test_should_raise_exception_when_template_doesnt_exist(self):
        self.assertRaises(TemplateDoesNotExist, render_to_string, 'simple.xyz')

    def _load_test_template(self, name):
        return open('hamlpy/test/templates/' + name, 'r').read()
