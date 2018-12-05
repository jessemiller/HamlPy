import importlib
import pytest

from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.test.utils import override_settings
from unittest import mock

from hamlpy.compiler import Compiler
from hamlpy.template import loaders


class LoaderTest(SimpleTestCase):
    def setUp(self):
        super(LoaderTest, self).setUp()

        importlib.reload(loaders)

    @mock.patch('hamlpy.template.loaders.Compiler', wraps=Compiler)
    def test_compiler_default_settings(self, mock_compiler_class):
        render_to_string('simple.hamlpy')

        mock_compiler_class.assert_called_once_with(options={})
        mock_compiler_class.reset_mock()

    @override_settings(HAMLPY_ATTR_WRAPPER='"', HAMLPY_DJANGO_INLINE_STYLE=False)
    def test_compiler_settings(self):
        importlib.reload(loaders)

        with mock.patch('hamlpy.template.loaders.Compiler', wraps=Compiler) as mock_compiler_class:
            rendered = render_to_string('simple.hamlpy')

            mock_compiler_class.assert_called_once_with(options={
                'attr_wrapper': '"',
                'django_inline_style': False
            })

            assert '"someClass"' in rendered

    def test_template_rendering(self):
        assert render_to_string('simple.hamlpy') == self._load_test_template('simple.html')

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
        with pytest.raises(TemplateDoesNotExist):
            render_to_string('simple.xyz')

    def _load_test_template(self, name):
        return open('hamlpy/test/templates/' + name, 'r').read()
