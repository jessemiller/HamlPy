from __future__ import print_function, unicode_literals

import regex
import six

from .attribute_dict_parser import AttributeDictParser


class Element(object):
    """contains the pieces of an element and can populate itself from haml element text"""

    self_closing_tags = ('meta', 'img', 'link', 'br', 'hr', 'input', 'source', 'track', 'area', 'base', 'col', 'command', 'embed', 'keygen', 'param', 'wbr')

    ELEMENT = '%'
    ID = '#'
    CLASS = '.'
    DEFAULT_TAG = 'div'

    ELEMENT_REGEX = regex.compile(r"""
        (?P<tag>%\w+(\:\w+)?)?
        (?P<id_and_classes>(\#|\.)\w[\w-]*)*
        (?P<attributes>\{.*\})?
        (?P<nuke_outer_whitespace>\>)?
        (?P<nuke_inner_whitespace>\<)?
        (?P<selfclose>/)?
        (?P<django>=)?
        (?P<inline>[^\w\.#\{].*)?
        """, regex.V1 | regex.X | regex.MULTILINE | regex.DOTALL | regex.UNICODE)

    def __init__(self, haml, attr_wrapper="'"):
        self.haml = haml
        self.attr_wrapper = attr_wrapper

        self.tag = self.DEFAULT_TAG
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
        components = self.ELEMENT_REGEX.search(self.haml).capturesdict()

        if components['tag']:
            self.tag = components.get('tag')[0].lstrip(self.ELEMENT)

        if components['attributes']:
            self.attributes_dict = AttributeDictParser(components.get('attributes')[0]).parse()
        else:
            self.attributes_dict = {}

        # parse ids and classes from the components
        ids = []
        classes = []

        for id_or_class in components.get('id_and_classes'):
            prefix = id_or_class[0]
            name = id_or_class[1:]
            if prefix == self.ID:
                ids.append(name)
            elif prefix == self.CLASS:
                classes.append(name)

        # include ids and classes in the attribute dictionary
        id_from_attrs = self.attributes_dict.get('id')
        if isinstance(id_from_attrs, tuple) or isinstance(id_from_attrs, list):
            ids += id_from_attrs
        elif isinstance(id_from_attrs, six.string_types):
            ids += [id_from_attrs]

        class_from_attrs = self.attributes_dict.get('class')
        if isinstance(class_from_attrs, tuple) or isinstance(class_from_attrs, list):
            classes += class_from_attrs
        elif isinstance(class_from_attrs, six.string_types):
            classes += [class_from_attrs]

        self.id = '_'.join(ids)
        self.classes = ' '.join(classes)

        self.self_close = components.get('selfclose') or (self.tag in self.self_closing_tags)

        self.nuke_inner_whitespace = bool(components.get('nuke_inner_whitespace'))
        self.nuke_outer_whitespace = bool(components.get('nuke_outer_whitespace'))
        self.django_variable = bool(components.get('django'))
        self.inline_content = components.get('inline')[0].strip() if components.get('inline') else ''

        self.attributes = self._render_attributes(self.attributes_dict, self.id, self.classes)

    def _render_attributes(self, dict, id, classes):
        attributes = []

        if len(id) > 0:
            attributes.append("id=%s" % self.attr_wrap(self.id))
        if len(classes) > 0:
            attributes.append("class=%s" % self.attr_wrap(self.classes))

        for k, v in dict.items():
            if k != 'id' and k != 'class':
                # Boolean attributes
                if v is None:
                    attributes.append("%s" % (k,))
                else:
                    value = self._escape_attribute_quotes(v)
                    attributes.append("%s=%s" % (k, self.attr_wrap(value)))

        return ' '.join(attributes)

    def _escape_attribute_quotes(self, v):
        """
        Escapes quotes with a backslash, except those inside a Django tag
        """
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
