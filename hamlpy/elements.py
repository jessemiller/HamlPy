import re
from attribute_dict_parser import AttributeDictParser

class Element(object):
    """contains the pieces of an element and can populate itself from haml element text"""
    
    self_closing_tags = ('meta', 'img', 'link', 'br', 'hr', 'input', 'source', 'track', 'area', 'base', 'col', 'command', 'embed', 'keygen', 'param', 'wbr')

    ELEMENT = '%'
    ID = '#'
    CLASS = '.'

    HAML_REGEX = re.compile(r"""
    (?P<tag>%\w+(\:\w+)?)?
    (?P<id>\#[\w-]*)?
    (?P<class>\.[\w\.-]*)*
    (?P<attributes>\{.*\})?
    (?P<nuke_outer_whitespace>\>)?
    (?P<nuke_inner_whitespace>\<)?
    (?P<selfclose>/)?
    (?P<django>=)?
    (?P<inline>[^\w\.#\{].*)?
    """, re.X|re.MULTILINE|re.DOTALL)


    def __init__(self, haml):
        self.haml = haml
        self.tag = None
        self.id = None
        self.classes = None
        self.attributes = ''
        self.self_close = False
        self.django_variable = False
        self.nuke_inner_whitespace = False
        self.nuke_outer_whitespace = False
        self.inline_content = ''
        self._parse_haml()
        
    def _parse_haml(self):
        split_tags = self.HAML_REGEX.search(self.haml).groupdict('')

        attribute_parser=AttributeDictParser(split_tags.get('attributes'))
        self.attributes_dict = attribute_parser.parse()
        self.attributes = self._render_attributes(self.attributes_dict)

        self.tag = split_tags.get('tag').strip(self.ELEMENT) or 'div'
        self.id = self._parse_id(split_tags.get('id'))
        self.classes = ('%s %s' % (split_tags.get('class').lstrip(self.CLASS).replace('.', ' '), self._parse_class_from_attributes_dict())).strip()
        self.self_close = split_tags.get('selfclose') or self.tag in self.self_closing_tags

        self.nuke_inner_whitespace = split_tags.get('nuke_inner_whitespace') != ''
        self.nuke_outer_whitespace = split_tags.get('nuke_outer_whitespace') != ''
        self.django_variable = split_tags.get('django') != ''
        self.inline_content = split_tags.get('inline').strip()

    def _parse_class_from_attributes_dict(self):
        clazz = self.attributes_dict.get('class', '')
        if not isinstance(clazz, str) and not isinstance(clazz, unicode):
            clazz = ''
            for one_class in self.attributes_dict.get('class'):
                clazz += ' '+one_class
        return clazz.strip()

    def _parse_id(self, id_haml):
        id_text = id_haml.strip(self.ID)
        if 'id' in self.attributes_dict:
            if len(id_text)>0:
                id_text += '_'
            id_text += self._parse_id_dict(self.attributes_dict['id'])
        return id_text
    
    def _parse_id_dict(self, id_dict):
        id_dict = self.attributes_dict.get('id')

        if isinstance(id_dict, tuple) or isinstance(id_dict, list):
            return '_'.join(id_dict)
        else:
            return id_dict

    def _render_attributes(self, dict):
        attributes=[]
        for k, v in dict.items():
            if k != 'id' and k != 'class':
                # Boolean attributes
                if v==None:
                    attributes.append( "%s" % (k,))
                else:
                    value = self._escape_attribute_quotes(v)
                    attributes.append( "%s='%s'" % (k, value))
                                       
        return ' '.join(attributes)
    
    
    def _escape_attribute_quotes(self,v):
        '''
        Escapes single quotes with a backslash, except those inside a Django tag
        '''
        escaped=[]
        inside_tag = False
        for i, _ in enumerate(v):
            if v[i:i+2] == '{%':
                inside_tag=True
            elif v[i:i+2] == '%}':
                inside_tag=False

            if v[i]=="'" and not inside_tag:
                escaped.append('\\')

            escaped.append(v[i])

        return ''.join(escaped)
