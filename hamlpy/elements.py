import re
import sys
from types import NoneType

class Conditional(object):

    """Data structure for a conditional construct in attribute dictionaries"""

    NOTHING = object()

    def __init__(self, test, body, orelse=NOTHING):
        self.test = test
        self.body = body
        self.orelse = orelse

    def __repr__(self):
        if self.orelse is self.NOTHING:
            attrs = [self.test, self.body]
        else:
            attrs = [self.test, self.body, self.orelse]
        return "<%s@0X%X %r>" % (self.__class__.__name__, id(self), attrs)

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
    ATTRIBUTE_REGEX = re.compile(r'(?P<pre>\{\s*|,\s*)%s\s*:\s*%s' % (_ATTRIBUTE_KEY_REGEX, _ATTRIBUTE_VALUE_REGEX), re.UNICODE)
    DJANGO_VARIABLE_REGEX = re.compile(r'^\s*=\s(?P<variable>[a-zA-Z_][a-zA-Z0-9._-]*)\s*$')

    # Attribute dictionary parsing
    ATTRKEY_REGEX = re.compile(r"\s*(%s|%s)\s*:\s*" % (
        _SINGLE_QUOTE_STRING_LITERAL_REGEX, _DOUBLE_QUOTE_STRING_LITERAL_REGEX),
        re.UNICODE)
    _VALUE_LIST_REGEX = r"\[\s*(?:(?:%s|%s|None(?!\w)|\d+)\s*,?\s*)*\]" % (
        _SINGLE_QUOTE_STRING_LITERAL_REGEX, _DOUBLE_QUOTE_STRING_LITERAL_REGEX)
    _VALUE_TUPLE_REGEX = r"\(\s*(?:(?:%s|%s|None(?!\w)|\d+)\s*,?\s*)*\)" % (
        _SINGLE_QUOTE_STRING_LITERAL_REGEX, _DOUBLE_QUOTE_STRING_LITERAL_REGEX)
    ATTRVAL_REGEX = re.compile(r"None(?!\w)|%s|%s|%s|%s|\d+" % (
        _SINGLE_QUOTE_STRING_LITERAL_REGEX, _DOUBLE_QUOTE_STRING_LITERAL_REGEX,
        _VALUE_LIST_REGEX, _VALUE_TUPLE_REGEX), re.UNICODE)

    CONDITION_REGEX = re.compile(r"(%s|%s|%s|%s|(?!,| else ).)+" % (
        _SINGLE_QUOTE_STRING_LITERAL_REGEX, _DOUBLE_QUOTE_STRING_LITERAL_REGEX,
        _VALUE_LIST_REGEX, _VALUE_TUPLE_REGEX), re.UNICODE)

    NEWLINE_REGEX = re.compile("[\r\n]+")


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
        if not isinstance(clazz, basestring):
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
        if isinstance(id_dict, basestring):
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
            attribute_dict_string = self.NEWLINE_REGEX.sub(" ", attribute_dict_string)
            try:
                # converting all allowed attributes to python dictionary style

                # Replace Ruby-style HAML with Python style
                attribute_dict_string = re.sub(self.RUBY_HAML_REGEX, '"\g<key>":', attribute_dict_string)
                # Put double quotes around key
                attribute_dict_string = re.sub(self.ATTRIBUTE_REGEX, '\g<pre>"\g<key>":\g<val>', attribute_dict_string)
                # Parse string as dictionary
                for (key, val) in self.parse_attr(attribute_dict_string[1:-1]):
                    if isinstance(val, Conditional):
                        if key not in ("id", "class"):
                            self.attributes += "{%% %s %%} " % val.test
                        value = "{%% %s %%}%s" % (val.test,
                            self.add_attr(key, val.body))
                        while isinstance(val.orelse, Conditional):
                            val = val.orelse
                            if key not in ("id", "class"):
                                self.attributes += "{%% el%s %%} " % val.test
                            value += "{%% el%s %%}%s" % (val.test,
                                self.add_attr(key, val.body))
                        if val.orelse is not val.NOTHING:
                            if key not in ("id", "class"):
                                self.attributes += "{% else %} "
                            value += "{%% else %%}%s" % self.add_attr(key,
                                val.orelse)
                        if key not in ("id", "class"):
                            self.attributes += "{% endif %}"
                        value += "{% endif %}"
                    else:
                        value = self.add_attr(key, val)
                    attributes_dict[key] = value
                self.attributes = self.attributes.strip()
            except Exception, e:
                raise Exception('failed to decode: %s' % attribute_dict_string)
                #raise Exception('failed to decode: %s. Details: %s'%(attribute_dict_string, e))

        return attributes_dict

    def parse_attr(self, string):
        """Generate (key, value) pairs from attributes dictionary string"""
        string = string.strip()
        while string:
            match = self.ATTRKEY_REGEX.match(string)
            if not match:
                raise SyntaxError("Dictionary key expected at %r" % string)
            key = eval(match.group(1))
            (val, string) = self.parse_attribute_value(string[match.end():])
            if string.startswith(","):
                string = string[1:].lstrip()
            yield (key, val)

    def parse_attribute_value(self, string):
        """Parse an attribute value from dictionary string

        Return a (value, tail) pair where tail is remainder of the string.

        """
        match = self.ATTRVAL_REGEX.match(string)
        if not match:
            raise SyntaxError("Dictionary value expected at %r" % string)
        val = eval(match.group(0))
        string = string[match.end():].lstrip()
        if string.startswith("if "):
            match = self.CONDITION_REGEX.match(string)
            # Note: cannot fail.  At least the "if" word must match.
            condition = match.group(0)
            string = string[len(condition):].lstrip()
            if string.startswith("else "):
                (orelse, string) = self.parse_attribute_value(
                    string[5:].lstrip())
                val = Conditional(condition, val, orelse)
            else:
                val = Conditional(condition, val)
        return (val, string)

    def add_attr(self, key, value):
        """Add attribute definition to self.attributes

        For "id" and "class" attributes, return attribute value
        (possibly modified by replacing deprecated syntax).

        For other attributes, return the "key=value" string
        appropriate for the value type and also add this string
        to self.attributes.

        """
        if isinstance(value, basestring):
            # DEPRECATED: Replace variable in attributes (e.g. "= somevar") with Django version ("{{somevar}}")
            newval = re.sub(self.DJANGO_VARIABLE_REGEX, '{{\g<variable>}}', value)
            if newval != value:
                sys.stderr.write("""
---------------------
DEPRECATION WARNING: %s
The Django attribute variable feature is deprecated
and may be removed in future versions.
Please use inline variables ={...} instead.
-------------------
""" % self.haml.lstrip())

            value = newval.decode('utf-8')
        if key in ("id", "class"):
            return value
        if isinstance(value, NoneType):
            attr = "%s" % key
        elif isinstance(value, int) or isinstance(value, float):
            attr = "%s=%s" % (key, self.attr_wrap(value))
        elif isinstance(value, basestring):
            attr = "%s=%s" % (key,
                self.attr_wrap(self._escape_attribute_quotes(value)))
        else:
            raise ValueError(
                "Non-scalar value %r (type %s) passed for HTML attribute %r"
                % (value, type(value), key))
        self.attributes += attr + " "
        return attr
