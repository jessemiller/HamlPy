from __future__ import print_function, unicode_literals

import os
import shutil
import sys
import unittest

from mock import patch

from hamlpy.hamlpy_watcher import watch_folder


WORKING_DIR = '.watcher_test'
INPUT_DIR = WORKING_DIR + os.sep + 'input'
OUTPUT_DIR = WORKING_DIR + os.sep + 'output'


class ScriptExit(Exception):
    def __init__(self, exit_code):
        self.exit_code = exit_code

    @classmethod
    def mock(cls, code):
        raise cls(code)


class WatcherTest(unittest.TestCase):

    def test_watch_folder(self):
        # remove working directory if it exists and re-create it
        if os.path.exists(WORKING_DIR):
            shutil.rmtree(WORKING_DIR)

        os.makedirs(INPUT_DIR)
        os.makedirs(OUTPUT_DIR)

        # create some haml files for testing
        self._write_file(INPUT_DIR + os.sep + 'test.haml', "%span{'class': 'test'}\n")
        self._write_file(INPUT_DIR + os.sep + 'error.haml', "%div{")

        # run as once off pass - should return 1 for number of failed conversions
        self._run_script(['hamlpy_watcher.py', INPUT_DIR, OUTPUT_DIR, '--once', '--input-extension=.haml'], 1)

        # check file without errors was converted
        output = self._read_file(OUTPUT_DIR + os.sep + 'test.html')
        self.assertEqual(output, "<span class='test'></span>\n")

    def _read_file(self, path):
        with open(path, 'r') as f:
            return f.read()

    def _write_file(self, path, text):
        with open(path, 'w') as f:
            f.write(text)

    def _run_script(self, script_args, expected_exit_code):
        # patch sys.exit so it throws an exception so we can return execution to this test
        with patch.object(sys, 'exit', side_effect=ScriptExit.mock):

            # patch sys.argv to pass our arguments to the script
            with patch.object(sys, 'argv', script_args):
                with self.assertRaises(ScriptExit) as raises:
                    watch_folder()

                assert raises.exception.exit_code == expected_exit_code
