from nodes import RootNode, create_node

class Compiler:

    def process(self, raw_text):
        split_text = raw_text.strip().split('\n')
        return self.process_lines(split_text)
        
    def process_lines(self, haml_lines):
        root = RootNode()
        for line in haml_lines:
            haml_node = create_node(line)
            root.add_node(haml_node)
        return root.render()

def convert_files():
    import sys
    import codecs
    
    if (len(sys.argv) < 2):
        print "Specify the input file as the first argument."
    else: 
        inFile = sys.argv[1]
        hamlLines = codecs.open(inFile, 'r', encoding='utf-8').read().splitlines()

        compiler = Compiler()
        output = compiler.processLines(hamlLines)
        
        if (len(sys.argv) == 3):
            outFile = open(sys.argv[2], 'w')
            outFile.write(output)
        else:
            print output
    
    
if __name__ == '__main__':
    convert_files()

