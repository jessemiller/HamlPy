import re

ELEMENT = '%'
ID = '#'
CLASS = '.'

SPECIAL_CHARACTERS = (ELEMENT, ID, CLASS)

class Compiler:

    def process(self, rawText):
        splitText = rawText.split('\n')
        return self.processLines(splitText)
        
    def processLines(self, hamlLines):
        rootNode = RootNode()
        for line in hamlLines:
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
    
    selfClosingTags = ('meta', 'img', 'link', 'script', 'br', 'hr')
    
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
        
        splitTags = re.search(r"(%\w+)(#\w*)?(\.[\w\.]*)*(\{.*\})?(/)?([^\w\.#\{].*)?", self.haml)
        tag = splitTags.groups()[0].strip(ELEMENT)
        idName = splitTags.groups()[1]
        className = splitTags.groups()[2]
        attributeDictionary = (splitTags.groups()[3] != None) and eval(splitTags.groups()[3]) or None
        selfCloseIt = splitTags.groups()[4] and True or False
        theRest = splitTags.groups()[5]
        
        if len(self.internalNodes) > 0:
            theRest = self.renderInternalNodes()
            
        if theRest == None:
            theRest = ''

        result = "<"+tag
        result += self.__getIdAttribute(idName, attributeDictionary)
        result += self.__getClassAttribute(className, attributeDictionary)
        if (attributeDictionary != None):
            for k, v in attributeDictionary.items():
                if (k != 'id' and k != 'class'):
                    result += " "+k+"='"+v+"'"
                    
        if ((tag in self.selfClosingTags or selfCloseIt) and not theRest.strip()):
            result += " />"
        else:
            result += ">%s</%s>" % (theRest.strip(), tag)
            
        return result

    def __getIdAttribute(self, idName, attributeDictionary):
        idNames = []
        if (idName != None):
            idNames.append(idName.strip('#'))
        if (attributeDictionary != None):
            for k, v in attributeDictionary.items():
                if (k == 'id' and isinstance(v, str)):
                    idNames.append(v)
                elif (k == 'id'):
                    for name in v:
                        idNames.append(name)
        
        idAttribute = ''
        if (len(idNames) > 0):
            idAttribute += " id='"
            first = True
            for name in idNames:
                if not first:
                    idAttribute += "_"
                idAttribute += name
                first = False
            idAttribute += "'"
            
        return idAttribute
    
    def __getClassAttribute(self, className, attributeDictionary):
        classAttribute = ''
        
        if (className != None):
            classAttribute += className.strip('.').replace('.',' ')
            
        if (attributeDictionary != None):
            for k, v in attributeDictionary.items():
                if (k == 'class' and isinstance(v, str)):
                    classAttribute += ' ' + v
                elif (k == 'class'):
                    for name in v:
                        classAttribute += ' ' + name
        
        if len(classAttribute) > 0:
            classAttribute = " class='%s'" % classAttribute.strip()
        
        return classAttribute
            