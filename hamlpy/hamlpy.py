#!/usr/bin/env python
from nodes import RootNode, FilterNode, HamlNode, create_node

class Compiler:
    def process(self, raw_text):
        split_text = raw_text.strip().split('\n')
        return self.process_lines(split_text)

    def process_lines(self, haml_lines):
        root = RootNode()
        line_iter = iter(haml_lines)

        for line_number, line in enumerate(line_iter):
            node_lines = line

            # Check for multi-line only when last node isn't FilterNode or when last node isn't parent of this node
            if (not(len(root.internal_nodes)>0 and isinstance(root.internal_nodes[-1], FilterNode))) or not root._should_go_inside_last_node(HamlNode(line)):
                if line.count('{') - line.count('}') == 1:
                    start_multiline=line_number # For exception handling

                    while line.count('{') - line.count('}') != -1:
                        try:
                            line = line_iter.next()
                        except StopIteration:
                            raise Exception('No closing brace found for multi-line HAML beginning at line %s' % (start_multiline+1))
                        node_lines += line
            haml_node = create_node(node_lines)
            root.add_node(haml_node)
        return root.render()

def convert_files():
    import sys
    import codecs
    
    if len(sys.argv) < 2:
        print "Specify the input file as the first argument."
    else: 
        infile = sys.argv[1]
        haml_lines = codecs.open(infile, 'r', encoding='utf-8').read().splitlines()

        compiler = Compiler()
        output = compiler.process_lines(haml_lines)
        
        if len(sys.argv) == 3:
            outfile = codecs.open(sys.argv[2], 'w', encoding='utf-8')
            outfile.write(output)
        else:
            print output
    
    
if __name__ == '__main__':
    convert_files()

