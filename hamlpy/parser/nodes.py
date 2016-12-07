from __future__ import print_function, unicode_literals

from .generic import ParseException, TreeNode, read_line, consume_whitespace, peek_indentation
from .elements import read_element
from .filters import get_filter


DOCTYPE_PREFIX = '!!!'
ELEMENT_PREFIXES = ('%', '#', '.')
HTML_COMMENT_PREFIX = '/'
CONDITIONAL_COMMENT_PREFIX = '/['
HAML_COMMENT_PREFIXES = ['-#', '=#']
VARIABLE_PREFIX = '='
TAG_PREFIX = '-'

HAML_ESCAPE = '\\'


def read_node(stream, prev, compiler):
    """
    Reads a node, returning either the node or None if we've reached the end of the input
    """
    while True:
        indent = consume_whitespace(stream)

        if stream.ptr >= stream.length:
            return None

        # empty lines are recorded as newlines on previous node
        if stream.text[stream.ptr] == '\n':
            if prev:
                prev.newlines += 1
            stream.ptr += 1
            continue

        # parse filter node
        if stream.text[stream.ptr] == ':':
            return read_filter_node(stream, indent, compiler)

        # peek ahead to differentiate between variable node starting #{.. and element node starting #\w...
        is_variable = stream.ptr < stream.length - 1 and stream.text[stream.ptr:stream.ptr+2] == '#{'

        if stream.text[stream.ptr] in ('%', '#', '.') and not is_variable:
            start = stream.ptr
            element = read_element(stream)
            haml = stream.text[start:stream.ptr]
            return ElementNode(indent + haml, compiler, element)

        line = read_line(stream)
        return Node.create(indent + line, compiler)


def read_filter_node(stream, indent, compiler):
    """
    Reads a filter node, e.g. :plain
    """
    assert stream.text[stream.ptr] == ':'

    stream.ptr += 1  # consume the initial colon
    name = read_line(stream)
    content_lines = []

    while stream.ptr < stream.length:
        line_indentation = peek_indentation(stream)

        if line_indentation is not None and line_indentation <= len(indent):
            break

        line = read_line(stream)

        # don't preserve whitespace on empty lines
        if line.isspace():
            line = ''

        content_lines.append(line)

    return FilterNode(indent, compiler, name, '\n'.join(content_lines))


class Node(TreeNode):
    """
    Base class of all nodes and also represents the root node
    """
    def __init__(self, compiler):
        super(Node, self).__init__()

        self.compiler = compiler

        self.indentation = -2
        self.newlines = 0        # number of empty lines to render after node
        self.before = ''         # rendered text at start of node, e.g. "<p>\n"
        self.after = ''          # rendered text at end of node, e.g. "\n</p>"
        self.empty_node = False  # indicates that a node does not render anything (for whitespace removal)

    @classmethod
    def create(cls, haml_line, compiler):
        """
        Creates a new node from the given line of Haml
        """
        stripped_line = haml_line.strip()

        inline_var_regex, escaped_var_regex = compiler.inline_variable_regexes

        if inline_var_regex.match(stripped_line) or escaped_var_regex.match(stripped_line):
            return PlaintextNode(haml_line, compiler)

        if stripped_line[0] == HAML_ESCAPE:
            return PlaintextNode(haml_line, compiler)

        if stripped_line.startswith(DOCTYPE_PREFIX):
            return DoctypeNode(haml_line, compiler)

        if stripped_line.startswith(CONDITIONAL_COMMENT_PREFIX):
            return ConditionalCommentNode(haml_line, compiler)

        if stripped_line[0] == HTML_COMMENT_PREFIX:
            return CommentNode(haml_line, compiler)

        for comment_prefix in HAML_COMMENT_PREFIXES:
            if stripped_line.startswith(comment_prefix):
                return HamlCommentNode(haml_line, compiler)

        if stripped_line[0] == VARIABLE_PREFIX:
            return VariableNode(haml_line, compiler)

        if stripped_line[0] == TAG_PREFIX:
            return TagNode(haml_line, compiler)

        return PlaintextNode(haml_line, compiler)

    def render(self):
        # Render (sets self.before and self.after)
        self._render_children()
        # Post-render (nodes can modify the rendered text of other nodes)
        self._post_render()
        # Generate HTML
        return self._generate_html()

    def render_newlines(self):
        return '\n' * (self.newlines + 1)

    def parent_of(self, node):
        if self._should_go_inside_last_node(node):
            ret = self.children[-1].parent_of(node)
            return ret
        else:
            return self

    def inside_filter_node(self):
        if self.parent:
            return self.parent.inside_filter_node()
        else:
            return False

    def _render_children(self):
        for child in self.children:
            child._render()

    def _post_render(self):
        for child in self.children:
            child._post_render()

    def _generate_html(self):
        output = [self.before]
        for child in self.children:
            output.append(child.before)
            output += [gc._generate_html() for gc in child.children]
            output.append(child.after)
        output.append(self.after)
        return ''.join(output)

    def add_node(self, node):
        if self._should_go_inside_last_node(node):
            self.children[-1].add_node(node)
        else:
            self.add_child(node)

    def _should_go_inside_last_node(self, node):
        return len(self.children) > 0 \
               and (node.indentation > self.children[-1].indentation
                    or (node.indentation == self.children[-1].indentation and self.children[-1].should_contain(node)))

    def should_contain(self, node):
        return False

    def debug_tree(self):  # pragma: no cover
        return '\n'.join(self._debug_tree([self]))

    def _debug_tree(self, nodes):  # pragma: no cover
        output = []
        for n in nodes:
            output.append('%s%s' % (' ' * (n.indentation + 2), n))
            if n.children:
                output += self._debug_tree(n.children)
        return output

    def __repr__(self):  # pragma: no cover
        return '%s' % type(self).__name__


class HamlNode(Node):
    def __init__(self, haml, compiler):
        super(HamlNode, self).__init__(compiler)

        self.haml = haml.strip()
        self.raw_haml = haml
        self.indentation = (len(haml) - len(haml.lstrip()))
        self.spaces = ''.join(haml[0] for i in range(self.indentation))

    def replace_inline_variables(self, content):
        inline_var_regex, escaped_var_regex = self.compiler.inline_variable_regexes

        content = inline_var_regex.sub(r'{{ \2 }}', content)
        content = escaped_var_regex.sub(r'\1', content)
        return content

    def __repr__(self):  # pragma: no cover
        return '%s(indent=%d, newlines=%d): %s' % (type(self).__name__, self.indentation, self.newlines, self.haml)


class PlaintextNode(HamlNode):
    """
    Node that is not modified or processed when rendering
    """
    def _render(self):
        text = self.replace_inline_variables(self.haml)

        # remove escape character unless inside filter node
        if text and text[0] == HAML_ESCAPE and not self.inside_filter_node():
            text = text.replace(HAML_ESCAPE, '', 1)

        self.before = '%s%s' % (self.spaces, text)
        if self.children:
            self.before += self.render_newlines()
        else:
            self.after = self.render_newlines()

        self._render_children()


class ElementNode(HamlNode):
    """
    An HTML tag node, e.g. %span
    """
    def __init__(self, haml, compiler, element):
        super(ElementNode, self).__init__(haml, compiler)

        self.element = element

    def _render(self):
        self.before = self._render_before(self.element)
        self.after = self._render_after(self.element)
        self._render_children()

    def _render_before(self, element):
        """
        Render opening tag and inline content
        """
        start = ["%s<%s" % (self.spaces, element.tag)]

        attributes = element.render_attributes(self.compiler.options['attr_wrapper'])
        if attributes:
            start.append(' ' + self.replace_inline_variables(attributes))

        content = self._render_inline_content(self.element.inline_content)

        if element.nuke_inner_whitespace and content:
            content = content.strip()

        if element.self_close and not content:
            start.append(" />")
        elif content:
            start.append(">%s" % content)
        elif self.children:
            start.append(">%s" % (self.render_newlines()))
        else:
            start.append(">")
        return ''.join(start)

    def _render_after(self, element):
        """
        Render closing tag
        """
        if element.inline_content:
            return "</%s>%s" % (element.tag, self.render_newlines())
        elif element.self_close:
            return self.render_newlines()
        elif self.children:
            return "%s</%s>\n" % (self.spaces, element.tag)
        else:
            return "</%s>\n" % element.tag

    def _post_render(self):
        # inner whitespace removal
        if self.element.nuke_inner_whitespace:
            self.before = self.before.rstrip()
            self.after = self.after.lstrip()

            if self.children:
                node = self
                # if node renders nothing, do removal on its first child instead
                if node.children[0].empty_node:
                    node = node.children[0]
                if node.children:
                    node.children[0].before = node.children[0].before.lstrip()

                node = self
                if node.children[-1].empty_node:
                    node = node.children[-1]
                if node.children:
                    node.children[-1].after = node.children[-1].after.rstrip()

        # outer whitespace removal
        if self.element.nuke_outer_whitespace:
            left_sibling = self.left_sibling()
            if left_sibling:
                # If node has left sibling, strip whitespace after left sibling
                left_sibling.after = left_sibling.after.rstrip()
                left_sibling.newlines = 0
            else:
                # If not, whitespace comes from it's parent node,
                # so strip whitespace before the node
                self.parent.before = self.parent.before.rstrip()
                self.parent.newlines = 0

            self.before = self.before.lstrip()
            self.after = self.after.rstrip()

            right_sibling = self.right_sibling()
            if right_sibling:
                right_sibling.before = right_sibling.before.lstrip()
            else:
                self.parent.after = self.parent.after.lstrip()
                self.parent.newlines = 0

        super(ElementNode, self)._post_render()

    def _render_inline_content(self, inline_content):
        if inline_content is None or len(inline_content) == 0:
            return None

        if self.element.django_variable:
            content = "{{ " + inline_content.strip() + " }}"
            return content
        else:
            return self.replace_inline_variables(inline_content)


class CommentNode(HamlNode):
    """
    An HTML comment node, e.g. / This is a comment
    """
    def _render(self):
        self.after = "-->\n"
        if self.children:
            self.before = "<!-- %s" % (self.render_newlines())
            self._render_children()
        else:
            self.before = "<!-- %s " % (self.haml.lstrip(HTML_COMMENT_PREFIX).strip())


class ConditionalCommentNode(HamlNode):
    """
    An HTML conditional comment node, e.g. /[if IE]
    """
    def _render(self):
        conditional = self.haml[1: self.haml.index(']') + 1]

        if self.children:
            self.before = "<!--%s>\n" % conditional
        else:
            content = self.haml[len(CONDITIONAL_COMMENT_PREFIX) + len(conditional) - 1:]
            self.before = "<!--%s>%s" % (conditional, content)

        self.after = "<![endif]-->\n"
        self._render_children()


class DoctypeNode(HamlNode):
    """
    An XML doctype node, e.g. !!! 5
    """
    def _render(self):
        doctype = self.haml.lstrip(DOCTYPE_PREFIX).strip()

        parts = doctype.split()
        if parts and parts[0] == "XML":
            attr_wrapper = self.compiler.options['attr_wrapper']
            encoding = parts[1] if len(parts) > 1 else 'utf-8'
            self.before = "<?xml version=%s1.0%s encoding=%s%s%s ?>" % (
                attr_wrapper, attr_wrapper,
                attr_wrapper, encoding, attr_wrapper,
            )
        else:
            types = {
                "": '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',  # noqa
                "Strict": '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',  # noqa
                "Frameset": '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">',  # noqa
                "5": '<!DOCTYPE html>',
                "1.1": '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'  # noqa
            }

            if doctype in types:
                self.before = types[doctype]

        self.after = self.render_newlines()


class HamlCommentNode(HamlNode):
    """
    A Haml comment node, e.g. -# This is a comment
    """
    def _render(self):
        self.after = self.render_newlines()[1:]

    def _post_render(self):
        pass


class VariableNode(HamlNode):
    """
    A Django variable node, e.g. =person.name
    """
    def __init__(self, haml, compiler):
        super(VariableNode, self).__init__(haml, compiler)

    def _render(self):
        tag_content = self.haml.lstrip(VARIABLE_PREFIX)
        self.before = "%s{{ %s }}" % (self.spaces, tag_content.strip())
        self.after = self.render_newlines()

    def _post_render(self):
        pass


class TagNode(HamlNode):
    """
    A Django/Jinja server-side tag node, e.g. -block
    """
    def __init__(self, haml, compiler):
        super(TagNode, self).__init__(haml, compiler)

        self.tag_statement = self.haml.lstrip(TAG_PREFIX).strip()
        self.tag_name = self.tag_statement.split(' ')[0]

        if self.tag_name in self.compiler.self_closing_tags.values():
            raise ParseException("Unexpected closing tag for self-closing tag %s" % self.tag_name)

    def _render(self):
        self.before = "%s{%% %s %%}" % (self.spaces, self.tag_statement)

        closing_tag = self.compiler.self_closing_tags.get(self.tag_name)

        if closing_tag:
            self.before += self.render_newlines()
            self.after = '%s{%% %s %%}%s' % (self.spaces, closing_tag, self.render_newlines())
        else:
            if self.children:
                self.before += self.render_newlines()
            else:
                self.after = self.render_newlines()
        self._render_children()

    def should_contain(self, node):
        return isinstance(node, TagNode) and node.tag_name in self.compiler.tags_may_contain.get(self.tag_name, '')


class FilterNode(HamlNode):
    """
    A type filter, e.g. :javascript
    """
    def __init__(self, indent, compiler, filter_name, content):
        super(FilterNode, self).__init__('', compiler)

        self.indentation = len(indent)
        self.spaces = indent
        self.filter_name = filter_name
        self.content = content

    def _render(self):
        filter_func = get_filter(self.filter_name)
        if not filter_func:
            raise ParseException("No such filter: " + self.filter_name)

        self.before = filter_func(self.content, self.spaces, self.compiler.options)
        self.after = self.render_newlines() if self.content else ''

    def _post_render(self):
        pass

    def __repr__(self):  # pragma: no cover
        return '%s(indent=%d, newlines=%d, filter=%s): %s' \
               % (type(self).__name__, self.indentation, self.newlines, self.filter_name, self.content)
