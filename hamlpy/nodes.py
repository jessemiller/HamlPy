import re

ELEMENT = '%'
ID = '#'
CLASS = '.'

HTML_COMMENT = '/'
HAML_COMMENT = '-#'

VARIABLE = '='
TAG = '-'

ELEMENT_CHARACTERS = (ELEMENT, ID, CLASS)

def createNode(hamlLine):
    strippedLine = hamlLine.strip()
    
    if (len(strippedLine) == 0):
        return None
    
    if strippedLine[0] in ELEMENT_CHARACTERS:
        return ElementNode(hamlLine)
    
    if strippedLine[0] == HTML_COMMENT:
        return CommentNode(hamlLine)
    
    if strippedLine.startswith(HAML_COMMENT):
        return HamlCommentNode(hamlLine)
    
    if strippedLine[0] == VARIABLE:
        return VariableNode(hamlLine)
    
    if strippedLine[0] == TAG:
        return TagNode(hamlLine)
     
    return HamlNode(hamlLine)

class RootNode:

    def __init__(self):
        self.indentation = -1
        self.internalNodes = []
 
    def addNode(self, hamlNode):
        if (hamlNode == None):
            return
        
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
    
    def hasInternalNodes(self):
        return (len(self.internalNodes) > 0)
    
class HamlNode(RootNode):
    
    def __init__(self, haml):
        RootNode.__init__(self)
        self.haml = haml.strip()
        self.rawHaml = haml
        self.indentation = (len(haml) - len(haml.lstrip()))
        
    def render(self):
        return self.haml
    
class ElementNode(HamlNode):
    
    selfClosingTags = ('meta', 'img', 'link', 'script', 'br', 'hr')
    
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        self.djangoVariable = False
 
    def render(self):
        return self.__renderTag()

    def __renderTag(self):
        
        splitTags = re.search(r"(%\w+)?(#\w*)?(\.[\w\.]*)*(\{.*\})?(/)?(=)?([^\w\.#\{].*)?", self.haml)
        tag = (splitTags.groups()[0] != None) and splitTags.groups()[0].strip(ELEMENT) or 'div'
        idName = splitTags.groups()[1]
        className = splitTags.groups()[2]
        attributeDictionary = (splitTags.groups()[3] != None) and eval(splitTags.groups()[3]) or None
        selfCloseIt = splitTags.groups()[4] and True or False
        self.djangoVariable = splitTags.groups()[5] and True or False
        tagContent = self.renderTagContent(splitTags.groups()[6])
        
        result = "<"+tag
        result += self.__getIdAttribute(idName, attributeDictionary)
        result += self.__getClassAttribute(className, attributeDictionary)
        if (attributeDictionary != None):
            for k, v in attributeDictionary.items():
                if (k != 'id' and k != 'class'):
                    result += " "+k+"='"+v+"'"
                    
        if ((tag in self.selfClosingTags or selfCloseIt) and not tagContent.strip()):
            result += " />"
        else:
            result += ">%s</%s>" % (tagContent.strip(), tag)
            
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

    def renderTagContent(self, currentTagContent):
        if self.hasInternalNodes():
            currentTagContent = self.renderInternalNodes()
        if currentTagContent == None:
            currentTagContent = ''
        if self.djangoVariable:
            currentTagContent = "{{ " + currentTagContent.strip() + " }}"
        return currentTagContent
    
class CommentNode(HamlNode):
    
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        self.haml = haml.strip().lstrip(HTML_COMMENT).strip()
        
    def render(self):
        content = ''
        if self.hasInternalNodes():
            content = self.renderInternalNodes()
        else:
            content = self.haml
        
        return "<!-- %s -->" % content

class HamlCommentNode(HamlNode):
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        
    def render(self):
        return ''

class VariableNode(ElementNode):
    def __init__(self, haml):
        ElementNode.__init__(self, haml)
        self.djangoVariable = True
        
    def render(self):
        tagContent = self.haml.lstrip(VARIABLE)
        return self.renderTagContent(tagContent)
    
class TagNode(HamlNode):
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        
    def render(self):
        tagContent = self.haml.lstrip(TAG)
        return "{%% %s %%}" % tagContent.strip()