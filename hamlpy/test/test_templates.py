import os
import codecs
import regex
import time
import unittest

from hamlpy.compiler import Compiler
from os import listdir, path


TEMPLATE_DIRECTORY = '/templates/'
TEMPLATE_EXTENSION = '.hamlpy'


class TemplateCheck(object):
    compiler = Compiler(options={'format': 'xhtml', 'escape_attrs': True})

    def __init__(self, name, haml, html):
        self.name = name
        self.haml = haml
        self.expected_html = html.replace('\r', '')  # ignore line ending differences
        self.actual_html = None

    @classmethod
    def load_all(cls):
        directory = os.path.dirname(__file__) + TEMPLATE_DIRECTORY
        tests = []

        # load all test files
        for f in listdir(directory):
            haml_path = path.join(directory, f)
            if haml_path.endswith(TEMPLATE_EXTENSION):
                html_path = path.splitext(haml_path)[0] + '.html'

                haml = codecs.open(haml_path, encoding='utf-8').read()
                html = open(html_path, 'r').read()

                tests.append(TemplateCheck(haml_path, haml, html))

        return tests

    def run(self):
        parsed = self.compiler.process(self.haml)

        # ignore line ending differences and blank lines
        self.actual_html = parsed.replace('\r', '')
        self.actual_html = regex.sub('\n[ \t]+(?=\n)', '\n', self.actual_html)

    def passed(self):
        return self.actual_html == self.expected_html


class TemplateCompareTest(unittest.TestCase):

    def test_templates(self):
        tests = TemplateCheck.load_all()

        for test in tests:
            print('Template test: ' + test.name)
            test.run()

            if not test.passed():
                print('\nHTML (actual): ')
                print('\n'.join(["%d. %s" % (i + 1, l) for i, l in enumerate(test.actual_html.split('\n'))]))
                self._print_diff(test.actual_html, test.expected_html)
                self.fail()

    @staticmethod
    def _print_diff(s1, s2):
        if len(s1) > len(s2):
            shorter = s2
        else:
            shorter = s1

        line = 1
        col = 1

        for i, _ in enumerate(shorter):
            if len(shorter) <= i + 1:
                print('Ran out of characters to compare!')
                print('Actual len=%d' % len(s1))
                print('Expected len=%d' % len(s2))
                break
            if s1[i] != s2[i]:
                print('Difference begins at line', line, 'column', col)
                actual_line = s1.splitlines()[line - 1]
                expected_line = s2.splitlines()[line - 1]
                print('HTML (actual, len=%2d)   : %s' % (len(actual_line), actual_line))
                print('HTML (expected, len=%2d) : %s' % (len(expected_line), expected_line))
                print('Character code (actual)  : %d (%s)' % (ord(s1[i]), s1[i]))
                print('Character code (expected): %d (%s)' % (ord(s2[i]), s2[i]))
                break

            if shorter[i] == '\n':
                line += 1
                col = 1
            else:
                col += 1
        else:
            print("No Difference Found")


def performance_test(num_runs):
    """
    Performance test which evaluates all the testing templates a given number of times
    """
    print("Loading all templates...")

    template_tests = TemplateCheck.load_all()

    print("Running templates tests...")

    times = []

    for r in range(num_runs):
        start = time.time()

        for test in template_tests:
            test.run()

        times.append(time.time() - start)

    print("Ran template tests %d times in %.2f seconds (average = %.3f secs)"
          % (num_runs, sum(times), sum(times) / float(num_runs)))


if __name__ == '__main__':
    performance_test(500)
