#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

import regex

from optparse import OptionParser

from hamlpy.parser.generic import Stream
from hamlpy.parser.nodes import Node, read_node

VALID_EXTENSIONS = ['haml', 'hamlpy']


class Compiler:
    DEFAULT_OPTIONS = {
        'attr_wrapper': '\'',            # how to render attribute values, e.g. foo='bar'
        'django_inline_style': True,     # support both #{...} and ={...}
        'tag_config': 'django',          # Django vs Jinja2 tags
        'custom_self_closing_tags': {},  # additional self-closing tags
        'debug_tree': False,
    }

    TAG_CONFIGS = {
        'django': {
            'self_closing': {
                'for': 'endfor',
                'if': 'endif',
                'ifchanged': 'endifchanged',
                'ifequal': 'endifequal',
                'ifnotequal': 'endifnotequal',
                'block': 'endblock',
                'filter': 'endfilter',
                'autoescape': 'endautoescape',
                'with': 'endwith',
                'blocktrans': 'endblocktrans',
                'spaceless': 'endspaceless',
                'comment': 'endcomment',
                'cache': 'endcache',
                'localize': 'endlocalize',
                'call': 'endcall',
                'macro': 'endmacro',
                'compress': 'endcompress'
            },
            'may_contain': {
                'if': ['else', 'elif'],
                'ifchanged': ['else'],
                'ifequal': ['else'],
                'ifnotequal': ['else'],
                'for': ['empty']
            }
        },
        'jinja2': {
            'self_closing': {
                'for': 'endfor',
                'if': 'endif',
                'block': 'endblock',
                'filter': 'endfilter',
                'with': 'endwith',
                'call': 'endcall',
                'macro': 'endmacro',
                'raw': 'endraw'
            },
            'may_contain': {
                'if': ['else', 'elif'],
                'for': ['empty', 'else']
            }
        }
    }

    def __init__(self, options=None):
        self.options = self.DEFAULT_OPTIONS.copy()
        if options:
            self.options.update(options)

        tag_config = self.TAG_CONFIGS[self.options['tag_config']]
        self.self_closing_tags = tag_config['self_closing']
        self.tags_may_contain = tag_config['may_contain']

        self.self_closing_tags.update(self.options['custom_self_closing_tags'])

        self.inline_variable_regexes = self._create_inline_variable_regexes()

    def process(self, haml):
        """
        Converts the given string of Haml to a regular Django HTML
        """
        stream = Stream(haml)

        root = Node(self.options)
        node = None

        while True:
            node = read_node(stream, root, prev=node, compiler=self)
            if not node:
                break

            root.add_node(node)

        if self.options['debug_tree']:  # pragma: no cover
            return root.debug_tree()
        else:
            return root.render()

    def _create_inline_variable_regexes(self):
        """
        Generates regular expressions for inline variables and escaped inline variables, based on compiler options
        """
        prefixes = ['=', '#'] if self.options['django_inline_style'] else ['#']
        prefixes = ''.join(prefixes)
        return (
            regex.compile(r'(?<!\\)([' + prefixes + r']\{\s*(.+?)\s*\})'),
            regex.compile(r'\\([' + prefixes + r']\{\s*(.+?)\s*\})')
        )


def convert_files():  # pragma: no cover
    import codecs

    parser = OptionParser()
    parser.add_option(
        "-d", "--debug-tree", dest="debug_tree",
        action="store_true",
        help="Print the generated tree instead of the HTML")
    parser.add_option(
        "--attr-wrapper", dest="attr_wrapper",
        type="choice", choices=('"', "'"), default="'",
        action="store",
        help="The character that should wrap element attributes. "
        "This defaults to ' (an apostrophe).")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        print("Specify the input file as the first argument.")
    else:
        infile = args[0]
        haml_lines = codecs.open(infile, 'r', encoding='utf-8').read().splitlines()

        compiler = Compiler(options.__dict__)
        output = compiler.process_lines(haml_lines)

        if len(args) == 2:
            outfile = codecs.open(args[1], 'w', encoding='utf-8')
            outfile.write(output)
        else:
            print(output)


if __name__ == '__main__':  # pragma: no cover
    convert_files()
