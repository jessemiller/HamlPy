import unittest
import mock
from hamlpy.hamlpy import Compiler

try:
    from django.conf import settings
    settings.configure(DEBUG=True, TEMPLATE_DEBUG=True)
except ImportError, e:
    pass

from hamlpy.template.loaders import get_haml_loader, TemplateDoesNotExist


class DummyLoader(object):
    """
    A dummy template loader that only loads templates from self.templates
    """
    templates = {
        "in_dict.txt": "Original txt contents",
        "loader_test.hamlpy": "Original hamlpy content",
    }

    def __init__(self, *args, **kwargs):
        self.Loader = self.__class__

    def get_contents(self, origin):
        if origin.template_name not in self.templates:
            raise TemplateDoesNotExist(origin.template_name)
        return self.templates[origin.template_name]

    def load_template_source(self, template_name, *args, **kwargs):
        if template_name not in self.templates:
            raise TemplateDoesNotExist(template_name)

        return self.templates[template_name], 'Original content'


class LoaderTest(unittest.TestCase):
    def setUp(self):
        dummy_loader = DummyLoader()
        hamlpy_loader_class = get_haml_loader(dummy_loader)
        self.hamlpy_loader = hamlpy_loader_class()

        patch_compiler_class = mock.patch('hamlpy.hamlpy.Compiler')
        self.compiler_class = patch_compiler_class.start()
        self.mock_compiler = mock.Mock(spec=Compiler)
        self.compiler_class.return_value = self.mock_compiler
        self.addCleanup(patch_compiler_class.stop)


class DummyOrigin(object):
    def __init__(self, name, template_name=None, loader=None):
        self.name = name
        self.template_name = template_name
        self.loader = loader


class LoadTemplateSourceTest(LoaderTest):
    """
    Tests for the django template loader. A dummy template loader is
    used that loads only from a dictionary of templates.
    """

    def _test_assert_exception(self, template_name):
        with self.assertRaises(TemplateDoesNotExist):
            self.hamlpy_loader.load_template_source(template_name)

    def test_file_not_in_dict(self):
        # not_in_dict.txt doesn't exit, so we're expecting an exception
        self._test_assert_exception('not_in_dict.hamlpy')

    def test_file_in_dict(self):
        # in_dict.txt in in dict, but with an extension not supported by
        # the loader, so we expect an exception
        self._test_assert_exception('in_dict.txt')

    def test_file_should_load(self):
        # loader_test.hamlpy is in the dict, so it should load fine
        self.hamlpy_loader.load_template_source('loader_test.hamlpy')
        self.mock_compiler.process.assert_called_with('Original hamlpy content')

    def test_file_different_extension(self):
        # loader_test.hamlpy is in dict, but we're going to try
        # to load loader_test.txt
        # we expect an exception since the extension is not supported by
        # the loader
        self._test_assert_exception('loader_test.txt')


class GetContentsTest(LoaderTest):
    def setUp(self):
        super(GetContentsTest, self).setUp()

    def _get_origin(self, template_name):
        return DummyOrigin(name='path/to/{}'.format(template_name), template_name=template_name)

    def test_it_raises_template_does_not_exist_with_invalid_template(self):
        origin = self._get_origin('not_in_dict.hamlpy')
        with self.assertRaises(TemplateDoesNotExist):
            self.hamlpy_loader.get_contents(origin)

    def test_it_does_parse_file_with_valid_extension(self):
        origin = self._get_origin(template_name='loader_test.hamlpy')
        self.hamlpy_loader.get_contents(origin)
        self.mock_compiler.process.assert_called_with('Original hamlpy content')

    def test_it_does_not_parse_file_with_invalid_extension(self):
        origin = self._get_origin(template_name='in_dict.txt')
        self.hamlpy_loader.get_contents(origin)
        self.assertIs(False, self.mock_compiler.process.called)

    def test_it_returns_the_parsed_content(self):
        origin = self._get_origin(template_name='loader_test.hamlpy')
        self.mock_compiler.process.return_value = 'Parsed content'

        parsed_content = self.hamlpy_loader.get_contents(origin)

        self.assertEqual('Parsed content', parsed_content)
