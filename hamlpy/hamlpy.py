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
    

