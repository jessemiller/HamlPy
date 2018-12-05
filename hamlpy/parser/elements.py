from collections import OrderedDict
from .attributes import read_attribute_dict
from .core import read_word, read_line


# non-word characters that we allow in tag names, ids and classes
DOM_OBJECT_EXTRA_CHARS = ('-',)


def read_tag(stream):
    """
    Reads an element tag, e.g. span, ng-repeat, cs:dropdown
    """
    part1 = read_word(stream, DOM_OBJECT_EXTRA_CHARS)

    if stream.ptr < stream.length and stream.text[stream.ptr] == ':':
        stream.ptr += 1
        part2 = read_word(stream, DOM_OBJECT_EXTRA_CHARS)
    else:
        part2 = None

    return (part1 + ':' + part2) if part2 else part1


def read_element(stream, compiler):
    """
    Reads an element, e.g. %span, #banner{style:"width: 100px"}, .ng-hide(foo=1)
    """
    assert stream.text[stream.ptr] in ('%', '.', '#')

    tag = None
    empty_class = False

    if stream.text[stream.ptr] == '%':
        stream.ptr += 1
        tag = read_tag(stream)

    elif stream.text[stream.ptr] == '.':
        # Element may start with a period representing an unidentified div rather than a CSS class. In this case it
        # can't have other classes or ids, e.g. .{foo:"bar"}
        next_ch = stream.text[stream.ptr + 1] if stream.ptr < stream.length - 1 else None
        if not (next_ch.isalnum() or next_ch == '_' or next_ch in DOM_OBJECT_EXTRA_CHARS):
            stream.ptr += 1
            empty_class = True

    _id = None
    classes = []

    if not empty_class:
        while stream.ptr < stream.length and stream.text[stream.ptr] in ('#', '.'):
            is_id = stream.text[stream.ptr] == '#'
            stream.ptr += 1

            id_or_class = read_word(stream, DOM_OBJECT_EXTRA_CHARS)
            if is_id:
                _id = id_or_class
            else:
                classes.append(id_or_class)

    attributes = OrderedDict()
    while stream.ptr < stream.length and stream.text[stream.ptr] in ('{', '('):
        attributes.update(read_attribute_dict(stream, compiler))

    if stream.ptr < stream.length and stream.text[stream.ptr] == '>':
        stream.ptr += 1
        nuke_outer_ws = True
    else:
        nuke_outer_ws = False

    if stream.ptr < stream.length and stream.text[stream.ptr] == '<':
        stream.ptr += 1
        nuke_inner_ws = True
    else:
        nuke_inner_ws = False

    if stream.ptr < stream.length and stream.text[stream.ptr] == '/':
        stream.ptr += 1
        self_close = True
    else:
        self_close = tag in Element.SELF_CLOSING

    if stream.ptr < stream.length and stream.text[stream.ptr] == '=':
        stream.ptr += 1
        django_variable = True
    else:
        django_variable = False

    if stream.ptr < stream.length:
        inline = read_line(stream)
        if inline is not None:
            inline = inline.strip()
    else:
        inline = None

    return Element(tag, _id, classes, attributes, nuke_outer_ws, nuke_inner_ws, self_close, django_variable, inline)


class Element(object):
    """
    An HTML element with an id, classes, attributes etc
    """
    SELF_CLOSING = (
        'meta', 'img', 'link', 'br', 'hr', 'input', 'source', 'track', 'area', 'base', 'col', 'command', 'embed',
        'keygen', 'param', 'wbr'
    )

    DEFAULT_TAG = 'div'

    def __init__(self, tag, _id, classes, attributes, nuke_outer_whitespace, nuke_inner_whitespace, self_close,
                 django_variable, inline_content):
        self.tag = tag or self.DEFAULT_TAG
        self.attributes = attributes
        self.nuke_inner_whitespace = nuke_inner_whitespace
        self.nuke_outer_whitespace = nuke_outer_whitespace
        self.self_close = self_close
        self.django_variable = django_variable
        self.inline_content = inline_content

        # merge ids from the attribute dictionary
        ids = [_id] if _id else []
        id_from_attrs = attributes.get('id')
        if isinstance(id_from_attrs, (tuple, list)):
            ids += id_from_attrs
        elif isinstance(id_from_attrs, str):
            ids += [id_from_attrs]

        # merge ids to a single value with _ separators
        self.id = '_'.join(ids) if ids else None

        # merge classes from the attribute dictionary
        class_from_attrs = attributes.get('class', [])
        if not isinstance(class_from_attrs, (tuple, list)):
            class_from_attrs = [class_from_attrs]

        self.classes = class_from_attrs + classes

    def render_attributes(self, options):
        def attr_wrap(val):
            return '%s%s%s' % (options.attr_wrapper, val, options.attr_wrapper)

        rendered = []

        for name, value in self.attributes.items():
            if name in ('id', 'class') or value in (None, False):
                # this line isn't recorded in coverage because it gets optimized away (http://bugs.python.org/issue2506)
                continue  # pragma: no cover

            if value is True:  # boolean attribute
                if options.xhtml:
                    rendered.append("%s=%s" % (name, attr_wrap(name)))
                else:
                    rendered.append(name)
            else:
                value = self._escape_attribute_quotes(value, options.attr_wrapper)
                rendered.append("%s=%s" % (name, attr_wrap(value)))

        if len(self.classes) > 0:
            rendered.append("class=%s" % attr_wrap(" ".join(self.classes)))

        if self.id:
            rendered.append("id=%s" % attr_wrap(self.id))

        return ' '.join(rendered)

    @staticmethod
    def _escape_attribute_quotes(v, attr_wrapper):
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

            if v[i] == attr_wrapper and not inside_tag:
                escaped.append('\\')

            escaped.append(v[i])

        return ''.join(escaped)
