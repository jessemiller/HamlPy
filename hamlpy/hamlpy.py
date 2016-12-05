#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

from hamlpy.parser.nodes import RootNode, HamlNode, TagNode, create_node

from optparse import OptionParser

VALID_EXTENSIONS = ['haml', 'hamlpy']


DEFAULT_OPTIONS = {
    'attr_wrapper': '\'',         # how to render attribute values, e.g. foo='bar'
    'django_inline_style': True,  # support both #{...} and ={...}
    'jinja': False,               # enable Jinja2 support
    'custom_self_closing': {},    # additional self-closing tags
    'debug_tree': False,
}


class Compiler:
    def __init__(self, options=None):
        self.options = DEFAULT_OPTIONS.copy()
        if options:
            self.options.update(options)

        # TODO keep list of tags on compiler and pass compiler rather than options to all nodes?
        TagNode.DJANGO_SELF_CLOSING.update(self.options['custom_self_closing'])

    def process(self, haml):
        """
        Converts the given string of Haml to a regular Django HTML
        """
        return self.process_lines(haml.split('\n'))

    def process_lines(self, haml_lines):
        """
        Converts the given list of lines of Haml to a regular Django HTML
        """
        root = RootNode(self.options)
        line_iter = iter(haml_lines)

        haml_node = None
        for line_number, line in enumerate(line_iter):
            node_lines = line

            if not root.parent_of(HamlNode(line, self.options)).inside_filter_node():
                if line.count('{') - line.count('}') == 1:
                    start_multiline = line_number  # for exception handling

                    while line.count('{') - line.count('}') != -1:
                        try:
                            line = next(line_iter)
                        except StopIteration:
                            raise Exception('No closing brace found for multi-line HAML beginning at line %s'
                                            % (start_multiline+1))
                        node_lines += line

            # Blank lines
            if haml_node is not None and len(node_lines.strip()) == 0:
                haml_node.newlines += 1
            else:
                haml_node = create_node(node_lines, self.options)
                if haml_node:
                    root.add_node(haml_node)

        if self.options['debug_tree']:  # pragma: no cover
            return root.debug_tree()
        else:
            return root.render()


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
