import textwrap

from .core import ParseException, TreeNode, read_line, read_whitespace, peek_indentation
from .elements import read_element
from .filters import get_filter


XHTML_DOCTYPES = {
    '1.1': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',  # noqa
    'strict': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',  # noqa
    'frameset': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">',  # noqa
    'mobile': '<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">',  # noqa
    'rdfa': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.0//EN" "http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd">',  # noqa
    'basic': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN" "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">',  # noqa
    '': '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',  # noqa
}

HTML4_DOCTYPES = {
    'strict': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">',
    'frameset': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">',
    '': '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
}


DOCTYPE_PREFIX = '!!!'
ELEMENT_PREFIXES = ('%', '#', '.')
HTML_COMMENT_PREFIX = '/'
CONDITIONAL_COMMENT_PREFIX = '/['
HAML_COMMENT_PREFIX = '-#'
VARIABLE_PREFIX = '='
TAG_PREFIX = '-'
FILTER_PREFIX = ':'

HAML_ESCAPE = '\\'


def read_node(stream, prev, compiler):
    """
    Reads a node, returning either the node or None if we've reached the end of the input
    """
    while True:
        indent = read_whitespace(stream)

        if stream.ptr >= stream.length:
            return None

        # convert indent to be all of the first character
        if indent:
            indent = indent[0] * len(indent)

        # empty lines are recorded as newlines on previous node
        if stream.text[stream.ptr] == '\n':
            if prev:
                prev.newlines += 1
            stream.ptr += 1
            continue

        # parse filter node
        if stream.text[stream.ptr] == FILTER_PREFIX:
            return read_filter_node(stream, indent, compiler)

        # peek ahead to so we don't try to parse an element from a variable node starting #{ or a Django tag ending %}
        if stream.text[stream.ptr] in ELEMENT_PREFIXES and stream.text[stream.ptr:stream.ptr+2] not in ('#{', '%}'):
            element = read_element(stream, compiler)
            return ElementNode(element, indent, compiler)

        # all other nodes are single line
        line = read_line(stream)

        inline_var_regex, escaped_var_regex = compiler.inline_variable_regexes

        if inline_var_regex.match(line) or escaped_var_regex.match(line):
            return PlaintextNode(line, indent, compiler)

        if line[0] == HAML_ESCAPE:
            return PlaintextNode(line, indent, compiler)

        if line.startswith(DOCTYPE_PREFIX):
            return DoctypeNode(line, indent, compiler)

        if line.startswith(CONDITIONAL_COMMENT_PREFIX):
            return ConditionalCommentNode(line, indent, compiler)

        if line[0] == HTML_COMMENT_PREFIX:
            return CommentNode(line, indent, compiler)

        if line.startswith(HAML_COMMENT_PREFIX):
            return HamlCommentNode(line, indent, compiler)

        if line[0] == VARIABLE_PREFIX:
            return VariableNode(line, indent, compiler)

        if line[0] == TAG_PREFIX:
            return TagNode(line, indent, compiler)

        return PlaintextNode(line, indent, compiler)


def read_filter_node(stream, indent, compiler):
    """
    Reads a filter node including its indented content, e.g. :plain
    """
    assert stream.text[stream.ptr] == FILTER_PREFIX

    stream.ptr += 1  # consume the initial colon
    name = read_line(stream)
    content_lines = []

    # read lines below with higher indentation as this filter's content
    while stream.ptr < stream.length:
        line_indentation = peek_indentation(stream)

        if line_indentation is not None and line_indentation <= len(indent):
            break

        line = read_line(stream)

        # don't preserve whitespace on empty lines
        if line.isspace():
            line = ''

        content_lines.append(line)

    return FilterNode(name.rstrip(), '\n'.join(content_lines), indent, compiler)


class Node(TreeNode):
    """
    Base class of all nodes
    """
    def __init__(self, indent, compiler):
        super(Node, self).__init__()

        if indent is not None:
            self.indent = indent
            self.indentation = len(indent)
        else:
            self.indent = None
            self.indentation = -1

        self.compiler = compiler

        self.newlines = 0        # number of empty lines to render after node
        self.before = ''         # rendered text at start of node, e.g. "<p>\n"
        self.after = ''          # rendered text at end of node, e.g. "\n</p>"

    @classmethod
    def create_root(cls, compiler):
        return cls(None, compiler)

    def render(self):
        # Render (sets self.before and self.after)
        self._render_children()
        # Post-render (nodes can modify the rendered text of other nodes)
        self._post_render()
        # Generate HTML
        return self._generate_html()

    def render_newlines(self):
        return '\n' * (self.newlines + 1)

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

    def replace_inline_variables(self, content):
        inline_var_regex, escaped_var_regex = self.compiler.inline_variable_regexes

        content = inline_var_regex.sub(r'{{ \2 }}', content)
        content = escaped_var_regex.sub(r'\1', content)
        return content

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


class LineNode(Node):
    """
    Base class of nodes which are a single line of Haml
    """
    def __init__(self, line, indent, compiler):
        super(LineNode, self).__init__(indent, compiler)

        self.haml = line.rstrip()

    def __repr__(self):  # pragma: no cover
        return '%s(indent=%d, newlines=%d): %s' % (type(self).__name__, self.indentation, self.newlines, self.haml)


class PlaintextNode(LineNode):
    """
    Node that is not modified or processed when rendering
    """
    def _render(self):
        text = self.replace_inline_variables(self.haml)

        # remove escape character
        if text and text[0] == HAML_ESCAPE:
            text = text.replace(HAML_ESCAPE, '', 1)

        self.before = '%s%s' % (self.indent, text)
        if self.children:
            self.before += self.render_newlines()
        else:
            self.after = self.render_newlines()

        self._render_children()


class ElementNode(Node):
    """
    An HTML tag node, e.g. %span
    """
    def __init__(self, element, indent, compiler):
        super(ElementNode, self).__init__(indent, compiler)

        self.element = element

    def _render(self):
        self.before = self._render_before(self.element)
        self.after = self._render_after(self.element)
        self._render_children()

    def _render_before(self, element):
        """
        Render opening tag and inline content
        """
        start = ["%s<%s" % (self.indent, element.tag)]

        attributes = element.render_attributes(self.compiler.options)
        if attributes:
            start.append(' ' + self.replace_inline_variables(attributes))

        content = self._render_inline_content(self.element.inline_content)

        if element.nuke_inner_whitespace and content:
            content = content.strip()

        if element.self_close and not content:
            start.append(">" if self.compiler.options.html else " />")
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
            return "%s</%s>\n" % (self.indent, element.tag)
        else:
            return "</%s>\n" % element.tag

    def _post_render(self):
        # inner whitespace removal
        if self.element.nuke_inner_whitespace:
            self.before = self.before.rstrip()
            self.after = self.after.lstrip()

            if self.children:
                node = self
                if node.children:
                    node.children[0].before = node.children[0].before.lstrip()

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


class CommentNode(LineNode):
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


class ConditionalCommentNode(LineNode):
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


class DoctypeNode(LineNode):
    """
    An XML doctype node, e.g. !!! 5
    """
    def _render(self):
        doctype = self.haml.lstrip(DOCTYPE_PREFIX).strip().lower()

        self.before = self.get_header(doctype, self.compiler.options)
        self.after = self.render_newlines()

    def get_header(self, doctype, options):
        if doctype.startswith('xml'):
            if options.html:
                return ''
            parts = doctype.split()
            encoding = parts[1] if len(parts) > 1 else 'utf-8'
            return "<?xml version=%s1.0%s encoding=%s%s%s ?>" % (
                options.attr_wrapper, options.attr_wrapper,
                options.attr_wrapper, encoding, options.attr_wrapper,
            )
        elif options.html5:
            return '<!DOCTYPE html>'
        elif options.xhtml:
            if doctype == "5":
                return '<!DOCTYPE html>'
            else:
                return XHTML_DOCTYPES.get(doctype, XHTML_DOCTYPES[''])
        else:
            return HTML4_DOCTYPES.get(doctype, HTML4_DOCTYPES[''])


class HamlCommentNode(LineNode):
    """
    A Haml comment node, e.g. -# This is a comment
    """
    def _render(self):
        self.after = self.render_newlines()[1:]

    def _post_render(self):
        pass


class VariableNode(LineNode):
    """
    A Django variable node, e.g. =person.name
    """
    def __init__(self, haml, indent, compiler):
        super(VariableNode, self).__init__(haml, indent, compiler)

    def _render(self):
        tag_content = self.haml.lstrip(VARIABLE_PREFIX)
        self.before = "%s{{ %s }}" % (self.indent, tag_content.strip())
        self.after = self.render_newlines()

    def _post_render(self):
        pass


class TagNode(LineNode):
    """
    A Django/Jinja server-side tag node, e.g. -block
    """
    def __init__(self, haml, indent, compiler):
        super(TagNode, self).__init__(haml, indent, compiler)

        self.tag_statement = self.haml.lstrip(TAG_PREFIX).strip()
        self.tag_name = self.tag_statement.split(' ')[0]

        if self.tag_name in self.compiler.self_closing_tags.values():
            raise ParseException("Unexpected closing tag for self-closing tag %s" % self.tag_name)

    def _render(self):
        self.before = "%s{%% %s %%}" % (self.indent, self.tag_statement)

        closing_tag = self.compiler.self_closing_tags.get(self.tag_name)

        if closing_tag:
            self.before += self.render_newlines()
            self.after = '%s{%% %s %%}%s' % (self.indent, closing_tag, self.render_newlines())
        else:
            if self.children:
                self.before += self.render_newlines()
            else:
                self.after = self.render_newlines()
        self._render_children()

    def should_contain(self, node):
        return isinstance(node, TagNode) and node.tag_name in self.compiler.tags_may_contain.get(self.tag_name, '')


class FilterNode(Node):
    """
    A type filter, e.g. :javascript
    """
    def __init__(self, filter_name, content, indent, compiler):
        super(FilterNode, self).__init__(indent, compiler)

        self.filter_name = filter_name
        self.content = content

    def _render(self):
        content = textwrap.dedent(self.content)

        filter_func = get_filter(self.filter_name)
        content = filter_func(content, self.compiler.options)

        content = self.indent + content.replace('\n', '\n' + self.indent)

        self.before = content
        self.after = self.render_newlines() if self.content else ''

    def _post_render(self):
        pass

    def __repr__(self):  # pragma: no cover
        return '%s(indent=%d, newlines=%d, filter=%s): %s' \
               % (type(self).__name__, self.indentation, self.newlines, self.filter_name, self.content)
