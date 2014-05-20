import unittest
import os
from hamlpy.ext import has_any_extension, _jinja2_available

class ExtTest(unittest.TestCase):
    """
    Tests for methods found in ../ext.py
    """
    
    def test_has_any_extension(self):
        extensions = [
            'hamlpy',
            'haml',
            '.txt'
        ]
        # no directory
        self.assertTrue(has_any_extension('dir.hamlpy', extensions))
        self.assertTrue(has_any_extension('dir.haml', extensions))
        self.assertTrue(has_any_extension('dir.txt', extensions))
        self.assertFalse(has_any_extension('dir.html', extensions))
        # with dot in filename
        self.assertTrue(has_any_extension('dir.dot.hamlpy', extensions))
        self.assertTrue(has_any_extension('dir.dot.haml', extensions))
        self.assertTrue(has_any_extension('dir.dot.txt', extensions))
        self.assertFalse(has_any_extension('dir.dot.html', extensions))
        
        # relative path
        self.assertTrue(has_any_extension('../dir.hamlpy', extensions))
        self.assertTrue(has_any_extension('../dir.haml', extensions))
        self.assertTrue(has_any_extension('../dir.txt', extensions))
        self.assertFalse(has_any_extension('../dir.html', extensions))
        # with dot in filename
        self.assertTrue(has_any_extension('../dir.dot.hamlpy', extensions))
        self.assertTrue(has_any_extension('../dir.dot.haml', extensions))
        self.assertTrue(has_any_extension('../dir.dot.txt', extensions))
        self.assertFalse(has_any_extension('../dir.dot.html', extensions))
        
        # absolute paths
        self.assertTrue(has_any_extension('/home/user/dir.hamlpy', extensions))
        self.assertTrue(has_any_extension('/home/user/dir.haml', extensions))
        self.assertTrue(has_any_extension('/home/user/dir.txt', extensions))
        self.assertFalse(has_any_extension('/home/user/dir.html', extensions))
        # with dot in filename
        self.assertTrue(has_any_extension('/home/user/dir.dot.hamlpy', extensions))
        self.assertTrue(has_any_extension('/home/user/dir.dot.haml', extensions))
        self.assertTrue(has_any_extension('/home/user/dir.dot.txt', extensions))
        self.assertFalse(has_any_extension('/home/user/dir.dot.html', extensions))

if _jinja2_available:
    import jinja2
    from hamlpy.ext import HamlPyTagExtension
    from nose.tools import eq_
    
    class JinjaHamlTagTest(unittest.TestCase):
        def _jinja_render(self, s, **kwargs):
            env = jinja2.Environment(extensions=[HamlPyTagExtension])
            
            return env.from_string(s).render(**kwargs)
        
        def test_empty_tag(self):
            haml = '{% haml %}{% endhaml %}'
            html = ''
            eq_(html, self._jinja_render(haml))
        
        def test_haml_tag(self):
            haml = '{% haml %}- if something\n   %p hello\n- else\n   %p goodbye{% endhaml %}'
            html = '\n   <p>goodbye</p>\n'
            eq_(html, self._jinja_render(haml))
        
        def test_haml_tag2(self):
            haml = 'before{% haml %}.header.span-24.last{% endhaml %}after'
            html = "before<div class='header span-24 last'></div>\nafter"
            eq_(html, self._jinja_render(haml))
        
        def test_error1(self):
            "jinja syntax error"
            haml = '{% haml %}'
            with self.assertRaises(jinja2.TemplateSyntaxError):
                self._jinja_render(haml)
        
        def test_error2(self):
            "haml syntax error"
            haml = '{% haml %}- endfor{% endhaml %}'
            with self.assertRaises(TypeError):
                self._jinja_render(haml)
