import re

class Element(object):
    """contains the pieces of an element and can populate itself from haml element text"""
    
    ELEMENT = '%'
    ID = '#'
    CLASS = '.'
    
    def __init__(self, haml):
        self.haml = haml
        self.tag = None
        self.id = None
        self.classes = None
        self._parse_haml()
        
    def _parse_haml(self):
        split_tags = re.search(r"(?P<tag>%\w+)?(?P<id>#\w*)?(?P<class>\.[\w\.]*)*(\{.*\})?(/)?(=)?([^\w\.#\{].*)?", self.haml).groupdict('')
        
        self.tag = split_tags.get('tag').strip(self.ELEMENT) or 'div'
        self.id = split_tags.get('id').strip(self.ID)
        self.classes = split_tags.get('class').lstrip(self.CLASS).replace('.', ' ')

        
        
