#!/usr/bin/env python
from __future__ import print_function, unicode_literals

from .nodes import RootNode, HamlNode, create_node
from optparse import OptionParser

VALID_EXTENSIONS=['haml', 'hamlpy']

class Compiler:

    def __init__(self, options_dict=None):
        options_dict = options_dict or {}
        self.debug_tree = options_dict.pop('debug_tree', False)
        self.options_dict = options_dict

    def process(self, raw_text):
        split_text = raw_text.split('\n')
        return self.process_lines(split_text)

    def process_lines(self, haml_lines):
        root = RootNode(**self.options_dict)
        line_iter = iter(haml_lines)

        haml_node=None
        for line_number, line in enumerate(line_iter):
            node_lines = line

            if not root.parent_of(HamlNode(line)).inside_filter_node():
                if line.count('{') - line.count('}') == 1:
                    start_multiline=line_number # For exception handling

                    while line.count('{') - line.count('}') != -1:
                        try:
                            line = next(line_iter)
                        except StopIteration:
                            raise Exception('No closing brace found for multi-line HAML beginning at line %s' % (start_multiline+1))
                        node_lines += line

            # Blank lines
            if haml_node is not None and len(node_lines.strip()) == 0:
                haml_node.newlines += 1
            else:
                haml_node = create_node(node_lines)
                if haml_node:
                    root.add_node(haml_node)

        if self.options_dict and self.options_dict.get('debug_tree'):
            return root.debug_tree()
        else:
            return root.render()

def convert_files():
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

if __name__ == '__main__':
    convert_files()
