import re


class Element(object):
    """contains the pieces of an element and can populate itself from haml element text"""
    
    self_closing_tags = ('meta', 'img', 'link', 'script', 'br', 'hr')

    ELEMENT = '%'
    ID = '#'
    CLASS = '.'

    HAML_REGEX = re.compile(r"(?P<tag>%\w+)?(?P<id>#\w*)?(?P<class>\.[\w\.-]*)*(?P<attributes>\{.*\})?(?P<selfclose>/)?(?P<django>=)?(?P<inline>[^\w\.#\{].*)?")
    
    def __init__(self, haml):
        self.haml = haml
        self.tag = None
        self.id = None
        self.classes = None
        self.attributes = ''
        self.self_close = False
        self.django_variable = False
        self.inline_content = ''
        self._parse_haml()
        
    def _parse_haml(self):
        split_tags = self.HAML_REGEX.search(self.haml).groupdict('')
        
        self.attributes_dict = self._parse_attribute_dictionary(split_tags.get('attributes'))
        self.tag = split_tags.get('tag').strip(self.ELEMENT) or 'div'
        self.id = self._parse_id(split_tags.get('id'))
        self.classes = ('%s %s' % (split_tags.get('class').lstrip(self.CLASS).replace('.', ' '), self._parse_class_from_attributes_dict())).strip()
        self.self_close = split_tags.get('selfclose') or self.tag in self.self_closing_tags
        self.django_variable = split_tags.get('django') != ''
        self.inline_content = split_tags.get('inline').strip()

    def _parse_class_from_attributes_dict(self):
        clazz = self.attributes_dict.get('class', '')
        if not isinstance(clazz, str):
            clazz = ''
            for one_class in self.attributes_dict.get('class'):
                clazz += ' '+one_class
        return clazz.strip()

    def _parse_id(self, id_haml):
        id_text = id_haml.strip(self.ID)
        if 'id' in self.attributes_dict:
            id_text += self._parse_id_dict(self.attributes_dict['id'])
        id_text = id_text.lstrip('_')
        return id_text
    
    def _parse_id_dict(self, id_dict):
        text = ''
        id_dict = self.attributes_dict.get('id')
        if isinstance(id_dict, str):
            text = '_'+id_dict
        else:
            text = ''
            for one_id in id_dict:
                text += '_'+one_id
        return text

    def _parse_attribute_dictionary(self, attribute_dict_string):        
        attributes_dict = {}
        if (attribute_dict_string):
            attributes_dict = eval(attribute_dict_string)
            for k, v in attributes_dict.items():
                if k != 'id' and k != 'class':
                    self.attributes += "%s='%s' " % (k, v)
            self.attributes = self.attributes.strip()
        return attributes_dict


        
        
