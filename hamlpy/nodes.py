import re
import sys
from StringIO import StringIO

from elements import Element

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer, guess_lexer_for_filename

ELEMENT = '%'
ID = '#'
CLASS = '.'
DOCTYPE = '!!!'

HTML_COMMENT = '/'
CONDITIONAL_COMMENT = '/['
HAML_COMMENTS = ['-#', '=#']

VARIABLE = '='
TAG = '-'

COFFEESCRIPT_FILTERS = [':coffeescript', ':coffee']
JAVASCRIPT_FILTER = ':javascript'
CSS_FILTER = ':css'
STYLUS_FILTER = ':stylus'
PLAIN_FILTER = ':plain'
PYTHON_FILTER = ':python'
CDATA_FILTER = ':cdata'
PYGMENTS_FILTER = ':highlight'

ELEMENT_CHARACTERS = (ELEMENT, ID, CLASS)

HAML_ESCAPE = '\\'

def create_node(haml_line):
    stripped_line = haml_line.strip()
    
    if not stripped_line:
        return None
        
    if stripped_line[0] == HAML_ESCAPE:
        return HamlNode(haml_line.replace(HAML_ESCAPE, '', 1))
        
    if stripped_line.startswith(DOCTYPE):
        return DoctypeNode(haml_line)
        
    if stripped_line[0] in ELEMENT_CHARACTERS:
        return ElementNode(haml_line)
    
    if stripped_line[0:len(CONDITIONAL_COMMENT)] == CONDITIONAL_COMMENT:
        return ConditionalCommentNode(haml_line)
        
    if stripped_line[0] == HTML_COMMENT:
        return CommentNode(haml_line)
    
    for comment_prefix in HAML_COMMENTS:
        if stripped_line.startswith(comment_prefix):
            return HamlCommentNode(haml_line)
    
    if stripped_line[0] == VARIABLE:
        return VariableNode(haml_line)

    if stripped_line[0] == TAG:
        return TagNode(haml_line)
    
    if stripped_line == JAVASCRIPT_FILTER:
        return JavascriptFilterNode(haml_line)
    
    if stripped_line in COFFEESCRIPT_FILTERS:
        return CoffeeScriptFilterNode(haml_line)
        
    if stripped_line == CSS_FILTER:
        return CssFilterNode(haml_line)
    
    if stripped_line == STYLUS_FILTER:
        return StylusFilterNode(haml_line)

    if stripped_line == PLAIN_FILTER:
        return PlainFilterNode(haml_line)
        
    if stripped_line == PYTHON_FILTER:
        return PythonFilterNode(haml_line)
    
    if stripped_line == CDATA_FILTER:
        return CDataFilterNode(haml_line)
		
	if stripped_line == PYGMENTS_FILTER:
		return PygmentsFilterNode(haml_line)
    
    return HamlNode(haml_line)

class RootNode:
    
    def __init__(self):
        self.indentation = -1
        self.internal_nodes = []
    
    def parent(self,node):
        if (node == None):
            return None

        if (self._should_go_inside_last_node(node)):
            ret = self.internal_nodes[-1].parent(node)
            return ret
        else:
            return self

    def add_node(self, node):
        if (node == None):
            return
        
        if (self._should_go_inside_last_node(node)):
            self.internal_nodes[-1].add_node(node)
        else:
            self.internal_nodes.append(node)
    
    def _should_go_inside_last_node(self, node):
        return len(self.internal_nodes)>0 and (node.indentation > self.internal_nodes[-1].indentation
            or (node.indentation == self.internal_nodes[-1].indentation and self.internal_nodes[-1].should_contain(node)))
    
    def render(self):
        return self.render_internal_nodes()
    
    def render_internal_nodes(self):
        return ''.join([node.render() for node in self.internal_nodes])
    
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
        self.spaces = ''.join(haml[0] for i in range(self.indentation))
    
    def render(self):
        return ''.join([self.spaces, self.haml, '\n', self.render_internal_nodes()])

    def __repr__(self):
        return '(%s) %s' % (self.__class__, self.haml)


class ElementNode(HamlNode):
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        self.django_variable = False
    
    def render(self):
        return self._render_tag()
    
    def _render_tag(self):
        element = Element(self.haml)
        self.django_variable = element.django_variable
        return self._generate_html(element)
        
    def _generate_html(self, element):        
        if self.indentation > 0:
            result = "%s<%s" % (self.spaces, element.tag) 
        else:
            result = "<%s" % element.tag 

        if element.id:
            result += " id='%s'" % element.id 
        if element.classes:
            result += " class='%s'" % element.classes 
        if element.attributes:
            result += ' ' + element.attributes            
            
        content = self._render_tag_content(element.inline_content)
        
        if element.self_close and not content:
            result += " />\n"
        else:
            result += ">%s</%s>\n" % (content, element.tag)
        
        return result
    
    def _render_tag_content(self, current_tag_content):
        if self.has_internal_nodes():
            current_tag_content = '\n' + self.render_internal_nodes() + self.spaces
        if current_tag_content == None:
            current_tag_content = ''
        if self.django_variable:
            current_tag_content = "{{ " + current_tag_content.strip() + " }}"
        current_tag_content = re.sub(r'#\{([a-zA-Z0-9\.\_]+)\}', r'{{ \1 }}', current_tag_content)
        return current_tag_content


class CommentNode(HamlNode):
    
    def render(self):
        content = ''
        if self.has_internal_nodes():
            content = '\n' + self.render_internal_nodes()
        else:
            content = self.haml.lstrip(HTML_COMMENT).strip() + ' '
        
        return "<!-- %s-->\n" % content

class ConditionalCommentNode(HamlNode):
    
    def render(self):
        conditional = self.haml[1: self.haml.index(']')+1 ]
        content = ''
        content = content + self.haml[self.haml.index(']')+1:]
        if self.has_internal_nodes():
            content = '\n' + self.render_internal_nodes()
        return "<!--%s>%s<![endif]-->" % (conditional, content)
        

class DoctypeNode(HamlNode):
    
    def render(self):
        doctype = self.haml.lstrip(DOCTYPE).strip()
        
        if doctype == "":
            content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        if doctype == "Strict":
            content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
        if doctype == "Frameset":
            content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">'
        if doctype == "5":
            content = '<!DOCTYPE html>'
        if doctype == "1.1":
            content = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
        
        return "%s\n" % content

class HamlCommentNode(HamlNode):
    
    def render(self):
        return ''


class VariableNode(ElementNode):
    def __init__(self, haml):
        ElementNode.__init__(self, haml)
        self.django_variable = True
    
    def render(self):
        tag_content = self.haml.lstrip(VARIABLE)
        return "%s%s\n" % (self.spaces, self._render_tag_content(tag_content))


class TagNode(HamlNode):
    self_closing = {'for':'endfor',
                    'if':'endif',
                    'ifchanged':'endifchanged',
                    'ifequal':'endifequal',
                    'ifnotequal':'endifnotequal',
                    'block':'endblock',
                    'filter':'endfilter',
                    'autoescape':'endautoescape',
                    'with':'endwith',
                    'blocktrans': 'endblocktrans',
                    'spaceless': 'endspaceless',
                    'comment': 'endcomment',
                    'cache': 'endcache',
                    'localize': 'endlocalize',
                    'compress': 'endcompress'}
    may_contain = {'if':['else', 'elif'], 
                   'ifchanged':'else',
                   'ifequal':'else',
                   'ifnotequal':'else',
                   'for':'empty', 
                   'with':'with'}
    
    def __init__(self, haml):
        HamlNode.__init__(self, haml)
        self.tag_statement = self.haml.lstrip(TAG).strip()
        self.tag_name = self.tag_statement.split(' ')[0]
        
        if (self.tag_name in self.self_closing.values()):
            raise TypeError("Do not close your Django tags manually.  It will be done for you.")
    
    def render(self):
        internal = self.render_internal_nodes()
        output = "%s{%% %s %%}\n%s" % (self.spaces, self.tag_statement, internal)
        if (self.tag_name in self.self_closing.keys()):
            output += '%s{%% %s %%}\n' % (self.spaces, self.self_closing[self.tag_name])
        return output
    
    def should_contain(self, node):
        return isinstance(node,TagNode) and node.tag_name in self.may_contain.get(self.tag_name,'')


class FilterNode(HamlNode):
  def add_node(self, node):
      if (node == None):
          return
      else:
          self.internal_nodes.append(node)


class PlainFilterNode(FilterNode):
    def render(self):
        if self.internal_nodes:
            first_indentation = self.internal_nodes[0].indentation
        return "".join([node.raw_haml[first_indentation:] + '\n' for node in self.internal_nodes])


class PythonFilterNode(FilterNode):
    def render(self):
        code = compile("".join([node.raw_haml.strip() + '\n' for node in self.internal_nodes]), "", "exec")
        
        buffer = StringIO()
        sys.stdout = buffer
        exec code
        # restore the original stdout
        sys.stdout = sys.__stdout__
        return buffer.getvalue()


class JavascriptFilterNode(FilterNode):
    def render(self):
        output = '<script type=\'text/javascript\'>\n// <![CDATA[\n'
        output += "".join((''.join((node.spaces, node.haml,'\n')) for node in self.internal_nodes))
        output += '// ]]>\n</script>\n'
        return output
        
        
class CoffeeScriptFilterNode(FilterNode):
    def render(self):
        output = '<script type=\'text/coffeescript\'>#<![CDATA[\n'
        output += ''.join([node.raw_haml for node in self.internal_nodes])
        output += '\n#]]></script>'
        return output


class CssFilterNode(FilterNode):
    def render(self):
        output = '<style type=\'text/css\'>\n/*<![CDATA[*/\n'
        output += "".join((''.join((node.spaces, node.haml,'\n')) for node in self.internal_nodes))
        output += '/*]]>*/\n</style>\n'
        return output


class StylusFilterNode(FilterNode):
    def render(self):
        output = '<style type=\'text/stylus\'>\n/*<![CDATA[*/\n'
        first_indentation = self.internal_nodes[0].indentation
        output += '\n'.join([node.raw_haml[first_indentation:] for node in self.internal_nodes])
        output += '\n/*]]>*/\n</style>\n'
        return output


class CDataFilterNode(FilterNode):
    def render(self):
        output = self.spaces + '<![CDATA[\n'
        output += "".join((''.join((node.spaces, node.haml,'\n')) for node in self.internal_nodes))
        output += self.spaces + ']]>\n'
        return output
		
class PygmentsFilterNode(FilterNode):
    def render(self):
        output = self.spaces
        output += highlighter(self.haml, guess_lexer(self.haml), HtmlFormatter())	
        return output
