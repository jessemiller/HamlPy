import re

ELEMENT = '%'
ID = '#'
CLASS = '.'

SPECIAL_CHARACTERS = (ELEMENT, ID, CLASS)

class Compiler:

    def process(self, rawText):
        rootNode = RootNode()
        splitText = rawText.split('\n')
        for line in splitText:
            hamlNode = HamlNode(line)
            rootNode.addNode(hamlNode)
        return rootNode.render()

class RootNode:

    def __init__(self):
        self.indentation = -1
        self.internalNodes = []
 
    def addNode(self, hamlNode):
        if (self.__shouldGoInsideLastNode(hamlNode)):
            self.internalNodes[-1].addNode(hamlNode)
        else:   
            self.internalNodes.append(hamlNode)

    def __shouldGoInsideLastNode(self, hamlNode):
        return len(self.internalNodes) > 0 and hamlNode.indentation > self.internalNodes[-1].indentation            
    
    def render(self):
        return self.renderInternalNodes()

    def renderInternalNodes(self):
        result = ''
        for node in self.internalNodes:
            result += node.render()
        return result
    
    
class HamlNode(RootNode):
    
    def __init__(self, haml):
        RootNode.__init__(self)
        self.haml = haml.strip()
        self.rawHaml = haml
        self.indentation = (len(haml) - len(haml.lstrip()))
 
    def render(self):
        result = ''
        if self.haml.startswith(ELEMENT):
            result = self.__renderTag()
        else:
            result = self.haml
        return result

    def __renderTag(self):
        tokens = self.haml.strip(ELEMENT).split(' ', 1)
        fullTag = tokens[0]
        
        theRest = ''
        if (len(tokens) > 1):
            theRest = tokens[1]
        
        if len(self.internalNodes) > 0:
            theRest = self.renderInternalNodes()
        
        splitTags = re.search(r"^([^#\.]+)(#.*)?(\..*)*", fullTag)
        tag = splitTags.groups()[0]
        idName = splitTags.groups()[1]
        className = splitTags.groups()[2]
        
        result = "<"+tag
        if (idName != None):
            result += " id='%s'" % idName.strip('#')
        if (className != None):
            result += " class='%s'" % className.strip('.')
        result += ">%s</%s>" % (theRest, tag)
        return result

    