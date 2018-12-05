import os
import shutil
import sys
import time
import unittest

from unittest.mock import patch

from hamlpy.hamlpy_watcher import watch_folder


WORKING_DIR = '.watcher_test'
INPUT_DIR = WORKING_DIR + os.sep + 'input'
OUTPUT_DIR = WORKING_DIR + os.sep + 'output'


class ScriptExit(Exception):
    def __init__(self, exit_code):
        self.exit_code = exit_code


class WatcherTest(unittest.TestCase):

    def test_watch_folder(self):
        # remove working directory if it exists and re-create it
        if os.path.exists(WORKING_DIR):
            shutil.rmtree(WORKING_DIR)

        os.makedirs(INPUT_DIR)

        # create some haml files for testing
        self._write_file(INPUT_DIR + os.sep + 'test.haml', "%span{'class': 'test'}\n- shoutout\n")
        self._write_file(INPUT_DIR + os.sep + 'error.haml', "%div{")
        self._write_file(INPUT_DIR + os.sep + '.#test.haml', "%hr")  # will be ignored

        # run as once off pass - should return 1 for number of failed conversions
        self._run_script([
            'hamlpy_watcher.py',
            INPUT_DIR, OUTPUT_DIR,
            '--once', '--input-extension=haml', '--verbose', '--tag=shoutout:endshoutout', '--django-inline', '--jinja'
        ], 1)

        # check file without errors was converted
        self.assertFileContents(OUTPUT_DIR + os.sep + 'test.html',
                                "<span class='test'></span>\n{% shoutout %}\n{% endshoutout %}\n")

        # check .#test.haml was ignored
        assert not os.path.exists(OUTPUT_DIR + os.sep + '.#test.html')

        # run without output directory which should make it default to re-using the input directory
        self._run_script([
            'hamlpy_watcher.py',
            INPUT_DIR,
            '--once', '--tag=shoutout:endshoutout'
        ], 1)

        self.assertFileContents(INPUT_DIR + os.sep + 'test.html',
                                "<span class='test'></span>\n{% shoutout %}\n{% endshoutout %}\n")

        # fix file with error
        self._write_file(INPUT_DIR + os.sep + 'error.haml', "%div{}")

        # check exit code is zero
        self._run_script(['hamlpy_watcher.py', INPUT_DIR, OUTPUT_DIR, '--once'], 0)

        # run in watch mode with 1 second refresh
        self._run_script([
            'hamlpy_watcher.py',
            INPUT_DIR,
            '--refresh=1', '--input-extension=haml', '--tag=shoutout:endshoutout'
        ], 1)

    def assertFileContents(self, path, contents):
        with open(path, 'r') as f:
            self.assertEqual(f.read(), contents)

    def _write_file(self, path, text):
        with open(path, 'w') as f:
            f.write(text)

    def _run_script(self, script_args, expected_exit_code):
        def raise_exception_with_code(code):
            raise ScriptExit(code)

        # patch sys.exit so it throws an exception so we can return execution to this test
        # patch sys.argv to pass our arguments to the script
        # patch time.sleep to be interrupted
        with patch.object(sys, 'exit', side_effect=raise_exception_with_code), patch.object(sys, 'argv', script_args), patch.object(time, 'sleep', side_effect=KeyboardInterrupt), self.assertRaises(ScriptExit) as raises:  # noqa

            watch_folder()

            assert raises.exception.exit_code == expected_exit_code
