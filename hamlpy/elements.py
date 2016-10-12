from __future__ import print_function, unicode_literals

import re
import six
import sys


class Element(object):
    """contains the pieces of an element and can populate itself from haml element text"""

    self_closing_tags = ('meta', 'img', 'link', 'br', 'hr', 'input', 'source', 'track')

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
    """, re.X | re.MULTILINE | re.DOTALL | re.UNICODE)

    _ATTRIBUTE_KEY_REGEX = r'(?P<key>[a-zA-Z_][a-zA-Z0-9_-]*)'
    #Single and double quote regexes from: http://stackoverflow.com/a/5453821/281469
    _SINGLE_QUOTE_STRING_LITERAL_REGEX = r"'([^'\\]*(?:\\.[^'\\]*)*)'"
    _DOUBLE_QUOTE_STRING_LITERAL_REGEX = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
    _ATTRIBUTE_VALUE_REGEX = r'(?P<val>\d+|None(?!\w)|%s|%s)' % (_SINGLE_QUOTE_STRING_LITERAL_REGEX, _DOUBLE_QUOTE_STRING_LITERAL_REGEX)

    RUBY_HAML_REGEX = re.compile(r'(:|\")%s(\"|) =>' % (_ATTRIBUTE_KEY_REGEX))
    SINGLE_VARIABLE_REGEX = re.compile(r'(?P<before>^{ *|, *)%s(?P<after> *}$| *, *)' % (_ATTRIBUTE_KEY_REGEX))
    ATTRIBUTE_REGEX = re.compile(r'(?P<pre>\{\s*|,\s*)%s\s*:\s*%s' % (_ATTRIBUTE_KEY_REGEX, _ATTRIBUTE_VALUE_REGEX), re.UNICODE)
    DJANGO_VARIABLE_REGEX = re.compile(r'^\s*=\s(?P<variable>[a-zA-Z_][a-zA-Z0-9._-]*)\s*$')


    def __init__(self, haml, attr_wrapper="'"):
        self.haml = haml
        self.attr_wrapper = attr_wrapper
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

    def attr_wrap(self, value):
        return '%s%s%s' % (self.attr_wrapper, value, self.attr_wrapper)

    def _parse_haml(self):
        split_tags = self.HAML_REGEX.search(self.haml).groupdict('')

        self.attributes_dict = self._parse_attribute_dictionary(split_tags.get('attributes'))
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
        if not isinstance(clazz, six.string_types):
            clazz = ''
            for one_class in self.attributes_dict.get('class'):
                clazz += ' ' + one_class
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
        if isinstance(id_dict, six.string_types):
            text = '_' + id_dict
        else:
            text = ''
            for one_id in id_dict:
                text += '_' + one_id
        return text

    def _escape_attribute_quotes(self, v):
        '''
        Escapes quotes with a backslash, except those inside a Django tag
        '''
        escaped = []
        inside_tag = False
        for i, _ in enumerate(v):
            if v[i:i + 2] == '{%':
                inside_tag = True
            elif v[i:i + 2] == '%}':
                inside_tag = False

            if v[i] == self.attr_wrapper and not inside_tag:
                escaped.append('\\')

            escaped.append(v[i])

        return ''.join(escaped)

    def _parse_attribute_dictionary(self, attribute_dict_string):
        attributes_dict = {}

        if (attribute_dict_string):
            attribute_dict_string = attribute_dict_string.replace('\n', ' ')
            try:
                # converting all allowed attributes to python dictionary style

                # When encountering single variables (like "required" or
                # "visible") set its value to None
                attribute_dict_string = re.sub(self.SINGLE_VARIABLE_REGEX, '\g<before>"\g<key>": None\g<after>', attribute_dict_string)

                # do it both because the regex is too greedy and doesn't do it
                # with single variable in between
                attribute_dict_string = re.sub(self.SINGLE_VARIABLE_REGEX, '\g<before>"\g<key>": None\g<after>', attribute_dict_string)

                # Replace Ruby-style HAML with Python style
                attribute_dict_string = re.sub(self.RUBY_HAML_REGEX, '"\g<key>":', attribute_dict_string)

                # Put double quotes around key
                attribute_dict_string = re.sub(self.ATTRIBUTE_REGEX, '\g<pre>"\g<key>":\g<val>', attribute_dict_string)

                # Parse string as dictionary
                attributes_dict = eval(attribute_dict_string)
                for k in sorted(attributes_dict.keys()):
                    v = attributes_dict[k]

                    if k != 'id' and k != 'class':
                        if v is None:
                            self.attributes += "%s " % (k,)
                        elif isinstance(v, int) or isinstance(v, float):
                            self.attributes += "%s=%s " % (k, self.attr_wrap(v))
                        else:
                            # DEPRECATED: Replace variable in attributes (e.g. "= somevar") with Django version ("{{somevar}}")
                            v = re.sub(self.DJANGO_VARIABLE_REGEX, '{{\g<variable>}}', attributes_dict[k])
                            if v != attributes_dict[k]:
                                sys.stderr.write("\n---------------------\nDEPRECATION WARNING: %s" % self.haml.lstrip() + \
                                                 "\nThe Django attribute variable feature is deprecated and may be removed in future versions." +
                                                 "\nPlease use inline variables ={...} instead.\n-------------------\n")

                            attributes_dict[k] = v

                            if isinstance(v, six.binary_type):
                                v = v.decode('utf-8')

                            self.attributes += "%s=%s " % (k, self.attr_wrap(self._escape_attribute_quotes(v)))
                self.attributes = self.attributes.strip()
            except Exception as e:
                raise Exception('failed to decode: %s' % attribute_dict_string)
                #raise Exception('failed to decode: %s. Details: %s'%(attribute_dict_string, e))

        return attributes_dict




