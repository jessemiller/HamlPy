import codecs
import unittest
from nose.tools import eq_
from hamlpy import hamlpy

class TestTemplateCompare(unittest.TestCase):

    def test_nuke_inner_whitespace(self):
        self._compare_test_files('nukeInnerWhiteSpace')

    def test_nuke_outer_whitespace(self):
        self._compare_test_files('nukeOuterWhiteSpace')

    def test_comparing_simple_templates(self):
        self._compare_test_files('simple')
        
    def test_mixed_id_and_classes_using_dictionary(self):
        self._compare_test_files('classIdMixtures')
    
    def test_self_closing_tags_close(self):
        self._compare_test_files('selfClosingTags')
        
    def test_nested_html_comments(self):
        self._compare_test_files('nestedComments')
        
    def test_haml_comments(self):
        self._compare_test_files('hamlComments')
        
    def test_implicit_divs(self):
        self._compare_test_files('implicitDivs')
        
    def test_django_combination_of_tags(self):
        self._compare_test_files('djangoCombo')
        
    def test_self_closing_django(self):
        self._compare_test_files('selfClosingDjango')
        
    def test_nested_django_tags(self):
        self._compare_test_files('nestedDjangoTags')
        
    def test_filters(self):
        self._compare_test_files('filters')
    
    def test_filters_markdown(self):
        try:
            import markdown
            self._compare_test_files('filtersMarkdown')
        except ImportError:
            pass

    def test_filters_pygments(self):
        try:
            import pygments
            if pygments.__version__ == '1.6':
                self._compare_test_files('filtersPygments16')
            else:
                self._compare_test_files('filtersPygments')
        except ImportError:
            pass

    def test_nested_if_else_blocks(self):
        self._compare_test_files('nestedIfElseBlocks')

    def test_all_if_types(self):
        self._compare_test_files('allIfTypesTest')

    def test_multi_line_dict(self):
        self._compare_test_files('multiLineDict')

    def test_filter_multiline_ignore(self):
        self._compare_test_files('filterMultilineIgnore')

    def test_whitespace_preservation(self):
        self._compare_test_files('whitespacePreservation')

    def _print_diff(self, s1, s2):
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

    def _compare_test_files(self, name):
        haml_lines = codecs.open('templates/' + name + '.hamlpy', encoding = 'utf-8').readlines()
        html = open('templates/' + name + '.html').read()
        
        haml_compiler = hamlpy.Compiler()
        parsed = haml_compiler.process_lines(haml_lines)

        # Ignore line ending differences
        parsed = parsed.replace('\r', '')
        html = html.replace('\r', '')
        
        if parsed != html:
            print('\nHTML (actual): ')
            print('\n'.join(["%d. %s" % (i + 1, l) for i, l in enumerate(parsed.split('\n')) ]))
            self._print_diff(parsed, html)
        eq_(parsed, html)
        
if __name__ == '__main__':
    unittest.main()
