from nodes import RootNode, createNode

class Compiler:

    def process(self, rawText):
        splitText = rawText.strip().split('\n')
        return self.processLines(splitText)
        
    def processLines(self, hamlLines):
        rootNode = RootNode()
        for line in hamlLines:
            hamlNode = createNode(line)
            rootNode.addNode(hamlNode)
        return rootNode.render()
    
if __name__ == '__main__':
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
    

