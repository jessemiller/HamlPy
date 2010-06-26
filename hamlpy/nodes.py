import re

ELEMENT = '%'
ID = '#'
CLASS = '.'

HTML_COMMENT = '/'
HAML_COMMENT = '-#'

VARIABLE = '='
TAG = '-'

ELEMENT_CHARACTERS = (ELEMENT, ID, CLASS)

def create_node(haml_line):
    stripped_line = haml_line.strip()
    
    if not stripped_line:
        return None
    
    if stripped_line[0] in ELEMENT_CHARACTERS:
        return ElementNode(haml_line)
    
    if stripped_line[0] == HTML_COMMENT:
        return CommentNode(haml_line)
    
    if stripped_line.startswith(HAML_COMMENT):
        return HamlCommentNode(haml_line)
    
    if stripped_line[0] == VARIABLE:
        return VariableNode(haml_line)
    
    if stripped_line[0] == TAG:
        return TagNode(haml_line)
    
    return HamlNode(haml_line)

class RootNode:
    
    def __init__(self):
        self.indentation = -1
        self.internal_nodes = []
    
    def add_node(self, node):
        if (node == None):
            return
        
        if (self._should_go_inside_last_node(node)):
            self.internal_nodes[-1].add_node(node)
        else:
            self.internal_nodes.append(node)
    
    def _should_go_inside_last_node(self, node):
        return self.internal_nodes and (node.indentation > self.internal_nodes[-1].indentation or self.internal_nodes[-1].should_contain(node))
    
    def render(self):
        return self.render_internal_nodes()
    
    def render_internal_nodes(self):
        result = ''
        for node in self.internal_nodes:
            result += node.render()
        return result
    
    def has_internal_nodes(self):
        return len(self.internal_nodes) > 0
    
    def should_contain(self, node):
        return False

class HamlNode(RootNode):
    
    def __init__(self, haml):
        RootNode.__init__(self)
        self.haml = haml.strip()
        self.raw_haml = haml
        self.indentation = (len(haml) - len(haml.lstrip()))
    
    def render(self):
        return self.haml

class ElementNode(HamlNode):
    
    self_closing_tags = ('meta', 'img', 'link', 'script', 'br', 'hr')
    
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        self.django_variable = False
    
    def render(self):
        return self.__renderTag()
    
    def __renderTag(self):
        
        split_tags = re.search(r"(%\w+)?(#\w*)?(\.[\w\.]*)*(\{.*\})?(/)?(=)?([^\w\.#\{].*)?", self.haml)
        tag = (split_tags.groups()[0] != None) and split_tags.groups()[0].strip(ELEMENT) or 'div'
        id_name = split_tags.groups()[1]
        class_name = split_tags.groups()[2]
        attribute_dict = (split_tags.groups()[3] != None) and eval(split_tags.groups()[3]) or None
        self_close_it = split_tags.groups()[4] and True or False
        self.django_variable = split_tags.groups()[5] and True or False
        tag_content = self.render_tag_content(split_tags.groups()[6])
        
        result = "<"+tag
        result += self._get_id_attribute(id_name, attribute_dict)
        result += self._get_class_attribute(class_name, attribute_dict)
        if (attribute_dict != None):
            for k, v in attribute_dict.items():
                if (k != 'id' and k != 'class'):
                    result += " "+k+"='"+v+"'"
        
        if ((tag in self.self_closing_tags or self_close_it) and not tag_content.strip()):
            result += " />"
        else:
            result += ">%s</%s>" % (tag_content.strip(), tag)
        
        return result
    
    def _get_id_attribute(self, id_name, attribute_dict):
        id_names = []
        if (id_name != None):
            id_names.append(id_name.strip('#'))
        if (attribute_dict != None):
            for k, v in attribute_dict.items():
                if (k == 'id' and isinstance(v, str)):
                    id_names.append(v)
                elif (k == 'id'):
                    for name in v:
                        id_names.append(name)
        
        id_attribute = ''
        if id_names:
            id_attribute += " id='"
            first = True
            for name in id_names:
                if not first:
                    id_attribute += "_"
                id_attribute += name
                first = False
            id_attribute += "'"
        
        return id_attribute
    
    def _get_class_attribute(self, class_name, attribute_dict):
        class_attribute = ''
        
        if (class_name != None):
            class_attribute += class_name.strip('.').replace('.',' ')
        
        if (attribute_dict != None):
            for k, v in attribute_dict.items():
                if (k == 'class' and isinstance(v, str)):
                    class_attribute += ' ' + v
                elif (k == 'class'):
                    for name in v:
                        class_attribute += ' ' + name
        
        if class_attribute:
            class_attribute = " class='%s'" % class_attribute.strip()
        
        return class_attribute
    
    def render_tag_content(self, current_tag_content):
        if self.has_internal_nodes():
            current_tag_content = self.render_internal_nodes()
        if current_tag_content == None:
            current_tag_content = ''
        if self.django_variable:
            current_tag_content = "{{ " + current_tag_content.strip() + " }}"
        return current_tag_content

class CommentNode(HamlNode):
    
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        self.haml = haml.strip().lstrip(HTML_COMMENT).strip()
    
    def render(self):
        content = ''
        if self.has_internal_nodes():
            content = self.render_internal_nodes()
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
        self.django_variable = True
    
    def render(self):
        tag_content = self.haml.lstrip(VARIABLE)
        return self.render_tag_content(tag_content)

class TagNode(HamlNode):
    self_closing = {'for':'endfor', 'if':'endif', 'block':'endblock'}
    
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        self.tag_statement = self.haml.lstrip(TAG).strip()
        self.tag_name = self.tag_statement.split(' ')[0]
        
        if (self.tag_name in self.self_closing.values()):
            raise TypeError("Do not close your Django tags manually.  It will be done for you.")
    
    def render(self):
        internal = self.render_internal_nodes()
        output = "{%% %s %%}%s" % (self.tag_statement, internal)
        if (self.tag_name in self.self_closing.keys()):
            output += '{%% %s %%}' % self.self_closing[self.tag_name]
        return output
    
    def should_contain(self, node):
        return (isinstance(node,TagNode) and node.tag_name == 'else')
        