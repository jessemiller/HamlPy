from __future__ import unicode_literals

import unittest
import os
from hamlpy.ext import has_any_extension

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