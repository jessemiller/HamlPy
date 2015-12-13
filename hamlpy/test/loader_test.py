import unittest
import sys

try:
  from django.conf import settings

  settings.configure(DEBUG=True, TEMPLATE_DEBUG=True)
except ImportError as e:
  pass

from hamlpy.template.loaders import get_haml_loader, TemplateDoesNotExist

class DummyLoader(object):
    """
    A dummy template loader that only loads templates from self.templates
    """
    templates = {
        "in_dict.txt" : "in_dict content",
        "loader_test.hamlpy" : "loader_test content",
    }
    def __init__(self, *args, **kwargs):
        self.Loader = self.__class__
    
    def load_template_source(self, template_name, *args, **kwargs):
        try:
            return (self.templates[template_name], "test:%s" % template_name)
        except KeyError:
            raise TemplateDoesNotExist(template_name)

class LoaderTest(unittest.TestCase):
    """
    Tests for the django template loader.
    
    A dummy template loader is used that loads only from a dictionary of templates.
    """
    
    def setUp(self): 
        dummy_loader = DummyLoader()
        
        hamlpy_loader_class = get_haml_loader(dummy_loader)
        self.hamlpy_loader = hamlpy_loader_class()
    
    def _test_assert_exception(self, template_name):
        try:
            self.hamlpy_loader.load_template_source(template_name)
        except TemplateDoesNotExist:
            self.assertTrue(True)
        else:
            self.assertTrue(False, '\'%s\' should not be loaded by the hamlpy tempalte loader.' % template_name)
    
    def test_file_not_in_dict(self):
        # not_in_dict.txt doesn't exit, so we're expecting an exception
        self._test_assert_exception('not_in_dict.hamlpy')
    
    def test_file_in_dict(self):
        # in_dict.txt in in dict, but with an extension not supported by
        # the loader, so we expect an exception
        self._test_assert_exception('in_dict.txt')
    
    def test_file_should_load(self):
        # loader_test.hamlpy is in the dict, so it should load fine
        try:
            self.hamlpy_loader.load_template_source('loader_test.hamlpy')
        except TemplateDoesNotExist:
            self.assertTrue(False, '\'loader_test.hamlpy\' should be loaded by the hamlpy tempalte loader, but it was not.')
        else:
            self.assertTrue(True)
    
    def test_file_different_extension(self):
        # loader_test.hamlpy is in dict, but we're going to try
        # to load loader_test.txt
        # we expect an exception since the extension is not supported by
        # the loader
        self._test_assert_exception('loader_test.txt')
