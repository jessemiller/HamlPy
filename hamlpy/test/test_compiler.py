import unittest

from hamlpy.compiler import Compiler
from hamlpy.parser import filters
from hamlpy.parser.core import ParseException


class CompilerTest(unittest.TestCase):

    def test_tags(self):
        # tags can have xml namespaces
        self._test("%fb:tag\n  content", "<fb:tag>\n  content\n</fb:tag>")

        # tags can have dashes
        self._test("%ng-tag\n  content", "<ng-tag>\n  content\n</ng-tag>")

    def test_ids_and_classes(self):
        # id on tag
        self._test('%div#someId Some text', "<div id='someId'>Some text</div>")

        # id with non-ascii characters
        self._test('%div#これはテストです test', "<div id='これはテストです'>test</div>")

        # class on tag
        self._test('%div.someClass Some text', "<div class='someClass'>Some text</div>")

        # class can contain dash
        self._test('.header.span-24.last', "<div class='header span-24 last'></div>")

        # multiple classes
        self._test('%div.someClass.anotherClass Some text', "<div class='someClass anotherClass'>Some text</div>")

        # class can come before id
        self._test('%div.someClass#someId', "<div class='someClass' id='someId'></div>")

    def test_attribute_dictionaries(self):
        # attribute dictionaries
        self._test("%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}",
                   "<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='en' lang='en'></html>")

        # attribute whitespace is ignored
        self._test('%form{ id : "myform" }', "<form id='myform'></form>")

        # HTML style
        self._test('%form(foo=bar id="myform")', "<form foo='{{ bar }}' id='myform'></form>")

        # multiple dicts
        self._test('%a(a="b"){:c => "d"} Stuff', "<a a='b' c='d'>Stuff</a>")

        self._test_error('%a(b=)', "Unexpected \")\". @ \"%a(b=)\" <-")

    def test_boolean_attributes(self):
        self._test("%input{required}", "<input required>")
        self._test("%input{required, a: 'b'}", "<input required a='b'>")
        self._test("%input{a: 'b', required, b: 'c'}", "<input a='b' required b='c'>")
        self._test("%input{a: 'b', required}", "<input a='b' required>")
        self._test("%input{checked, required, visible}", "<input checked required visible>")
        self._test("%input(checked=true)", "<input checked>")
        self._test("%input(checked=true)", "<input checked='checked' />", options={'format': 'xhtml'})

    def test_attribute_values_as_tuples_and_lists(self):
        # id attribute as tuple
        self._test("%div{'id':('itemType', '5')}",  "<div id='itemType_5'></div>")

        # attributes as lists
        self._test("%div{'id':['Article','1'], 'class':['article','entry','visible']} Booyaka",
                   "<div class='article entry visible' id='Article_1'>Booyaka</div>")
        self._test("%div{'id': ('article', '3'), 'class': ('newest', 'urgent')} Content",
                   "<div class='newest urgent' id='article_3'>Content</div>")

    def test_comments(self):
        self._test('/ some comment', "<!-- some comment -->")

        # comments should hide child nodes
        self._test('''
-# My comment
  #my_div
    my text
test''', "test")

        # conditional comments
        self._test("/[if IE] You use a shitty browser", "<!--[if IE]> You use a shitty browser<![endif]-->")
        self._test("/[if IE]\n  %h1 You use a shitty browser",
                   "<!--[if IE]>\n  <h1>You use a shitty browser</h1>\n<![endif]-->")
        self._test('/[if lte IE 7]\n\ttest\n#test',
                   "<!--[if lte IE 7]>\n\ttest\n<![endif]-->\n<div id='test'></div>")

    def test_django_variables(self):
        # whole-line variable with =
        self._test('= story.tease', '{{ story.tease }}')

        # element content variable with =
        self._test('%div= story.tease', '<div>{{ story.tease }}</div>')

        # embedded Django variables using #{...}
        self._test("#{greeting} #{name}, how are you #{date}?",
                   "{{ greeting }} {{ name }}, how are you {{ date }}?")
        self._test("%h1 Hello, #{person.name}, how are you?", "<h1>Hello, {{ person.name }}, how are you?</h1>")

        # embedded Django variables using ={...} (not enabled by default)
        self._test("Hi ={name}, how are you?", "Hi ={name}, how are you?")
        self._test("Hi ={name}, how are you?", "Hi {{ name }}, how are you?",
                   options={'django_inline_style': True})

        # variables can use Django filters
        self._test("#{value|center:\"15\"}", "{{ value|center:\"15\" }}")

        # variables can be used in attribute values
        self._test("%a{'b': '#{greeting} test'} blah", "<a b='{{ greeting }} test'>blah</a>")

        # including in the id or class
        self._test("%div{'id':'package_#{object.id}'}", "<div id='package_{{ object.id }}'></div>")
        self._test("%div{'class':'package_#{object.id}'}", "<div class='package_{{ object.id }}'></div>")

        # they can be escaped
        self._test("%a{'b': '\\\\#{greeting} test', title: \"It can't be removed\"} blah",
                   "<a b='#{greeting} test' title='It can&#39;t be removed'>blah</a>")
        self._test("%h1 Hello, \\={name}, how are you ={ date }?",
                   "<h1>Hello, ={name}, how are you {{ date }}?</h1>", options={'django_inline_style': True})
        self._test("\\#{name}, how are you?", "#{name}, how are you?")

    def test_django_tags(self):
        # if/else
        self._test('- if something\n   %p hello\n- else\n   %p goodbye',
                   '{% if something %}\n   <p>hello</p>\n{% else %}\n   <p>goodbye</p>\n{% endif %}')

        # with
        self._test('- with thing1 as another\n  stuff',
                   '{% with thing1 as another %}\n  stuff\n{% endwith %}')
        self._test('- with context\n  hello\n- with other_context\n  goodbye',
                   '{% with context %}\n  hello\n{% endwith %}\n{% with other_context %}\n  goodbye\n{% endwith %}')

        # trans
        self._test('- trans "Hello"\n', '{% trans "Hello" %}')

        # blocktrans
        self._test('- blocktrans with amount=num_cookies\n'
                   '  There are #{ amount } cookies',
                   '{% blocktrans with amount=num_cookies %}\n'
                   '  There are {{ amount }} cookies\n'
                   '{% endblocktrans %}')
        self._test('- blocktrans with amount=num_cookies\n'
                   '  There is one cookie\n'
                   '- plural\n'
                   '  There are #{ amount } cookies',
                   '{% blocktrans with amount=num_cookies %}\n'
                   '  There is one cookie\n'
                   '{% plural %}\n'
                   '  There are {{ amount }} cookies\n'
                   '{% endblocktrans %}')

        # exception using a closing tag of a self-closing tag
        parser = Compiler()
        self.assertRaises(ParseException, parser.process, '- endfor')

    def test_plain_text(self):
        self._test("This should be plain text", "This should be plain text")
        self._test("This should be plain text\n    This should be indented",
                   "This should be plain text\n    This should be indented")

        # native Django tags {% %} should be treated as plain text
        self._test("text   {%\n  trans ''\n%}", "text   {%\n  trans ''\n%}")
        self._test("text\n   {%\n  trans ''\n%}", "text\n   {%\n  trans ''\n%}")

    def test_plain_filter(self):
        # with indentation
        self._test(":plain\n    -This should be plain text\n    .This should be more\n      This should be indented",
                   "-This should be plain text\n.This should be more\n  This should be indented")

        # with no children
        self._test(":plain\nNothing", "Nothing")

        # with escaped back slash
        self._test(":plain\n  \\Something", "\\Something")

        # with space after filter name
        self._test(":plain \n    -This should be plain text\n",
                   "-This should be plain text")

    def test_preserve_filter(self):
        # with indentation
        self._test(":preserve\n    -This should be plain text\n    .This should be more\n      This should be indented",
                   "-This should be plain text&#x000A;.This should be more&#x000A;  This should be indented")

        # with no children
        self._test(":preserve\nNothing", "Nothing")

        # with escaped back slash
        self._test(":preserve\n  \\Something", "\\Something")

    def test_python_filter(self):
        self._test(":python\n", '')  # empty
        self._test(":python\n   for i in range(0, 5): print(\"<p>item \\%s</p>\" % i)",
                   '<p>item \\0</p>\n<p>item \\1</p>\n<p>item \\2</p>\n<p>item \\3</p>\n<p>item \\4</p>')

        self._test_error(":python\n   print(10 / 0)", "Error whilst executing python filter node", ZeroDivisionError)

    def test_pygments_filter(self):
        self._test(":highlight\n", '')  # empty
        self._test(":highlight\n  print(1)\n", '<div class="highlight"><pre><span></span><span class="k">print</span><span class="p">(</span><span class="mi">1</span><span class="p">)</span>\n</pre></div>')  # noqa

        filters._pygments_available = False

        self._test_error(":highlight\n  print(1)\n", "Pygments is not available")

        filters._pygments_available = True

    def test_markdown_filter(self):
        self._test(":markdown\n", '')  # empty
        self._test(":markdown\n  *Title*\n", '<p><em>Title</em></p>')

        filters._markdown_available = False

        self._test_error(":markdown\n  *Title*\n", "Markdown is not available")

        filters._markdown_available = True

    def test_invalid_filter(self):
        self._test_error(":nosuchfilter\n", "No such filter: nosuchfilter")

    def test_doctypes(self):
        self._test('!!!', '<!DOCTYPE html>', options={'format': 'html5'})
        self._test('!!! 5', '<!DOCTYPE html>', options={'format': 'xhtml'})
        self._test('!!! 5', '<!DOCTYPE html>')
        self._test('!!! strict', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',  # noqa
                   options={'format': 'xhtml'})
        self._test('!!! frameset', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">',  # noqa
                   options={'format': 'xhtml'})
        self._test('!!! mobile', '<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">',  # noqa
                   options={'format': 'xhtml'})
        self._test('!!! basic', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN" "http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd">',  # noqa
                   options={'format': 'xhtml'})
        self._test('!!! transitional', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',  # noqa
                   options={'format': 'xhtml'})
        self._test('!!!', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',  # noqa
                   options={'format': 'xhtml'})
        self._test('!!! strict', '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">',  # noqa
                   options={'format': 'html4'})
        self._test('!!! frameset', '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">',  # noqa
                   options={'format': 'html4'})
        self._test('!!! transitional', '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',  # noqa
                   options={'format': 'html4'})
        self._test('!!!', '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',  # noqa
                   options={'format': 'html4'})

        self._test('!!! XML', '', options={'format': 'html4'})
        self._test('!!! XML iso-8589', "<?xml version='1.0' encoding='iso-8589' ?>",
                   options={'format': 'xhtml'})

    def test_attr_wrapper(self):
        self._test("%p{ :strange => 'attrs'}", "<p strange=*attrs*></p>",
                   options={'attr_wrapper': '*', 'escape_attrs': True})
        self._test("%p{ :escaped => 'quo\"te'}", "<p escaped=\"quo&quot;te\"></p>",
                   options={'attr_wrapper': '"', 'escape_attrs': True})
        self._test("%p{ :escaped => 'quo\\'te'}", "<p escaped=\"quo&#39;te\"></p>",
                   options={'attr_wrapper': '"', 'escape_attrs': True})
        self._test("%p{ :escaped => 'q\\'uo\"te'}", "<p escaped=\"q&#39;uo&quot;te\"></p>",
                   options={'attr_wrapper': '"', 'escape_attrs': True})
        self._test("!!! XML", "<?xml version=\"1.0\" encoding=\"utf-8\" ?>",
                   options={'attr_wrapper': '"', 'format': 'xhtml', 'escape_attrs': True})

    def test_attr_escaping(self):
        self._test("""#foo{:class => '<?php echo "&quot;" ?>'}""",
                   """<div class='<?php echo "&quot;" ?>' id='foo'></div>""",
                   options={'escape_attrs': False})
        self._test("""#foo{:class => '"&lt;&gt;&amp;"'}""",
                   """<div class='&quot;&amp;lt;&amp;gt;&amp;amp;&quot;' id='foo'></div>""",
                   options={'escape_attrs': True})
        self._test("""#foo{:class => '{% trans "Hello" %}'}""",
                   """<div class='{% trans "Hello" %}' id='foo'></div>""",
                   options={'escape_attrs': True})

    def test_node_escaping(self):
        self._test("\\= Escaped", "= Escaped")
        self._test("\\%}", "%}")
        self._test("  \\:python", "  :python")

    def test_utf8(self):
        self._test("%a{'href':'', 'title':'링크(Korean)'} Some Link",
                   "<a href='' title='\ub9c1\ud06c(Korean)'>Some Link</a>")

    def test_custom_filter(self):
        def upper(text, options):
            return text.upper()

        filters.register_filter('upper', upper)

        self._test(":upper\n  welcome", 'WELCOME')

    def _test(self, haml, expected_html, options=None):
        if not options:
            options = {'escape_attrs': True}

        compiler = Compiler(options)
        result = compiler.process(haml)

        result = result.rstrip('\n')  # ignore trailing new lines

        assert result == expected_html

    def _test_error(self, haml, expected_message, expected_cause=None, compiler_options=None):
        compiler = Compiler(compiler_options)

        try:
            compiler.process(haml)
            self.fail("Expected exception to be raised")
        except Exception as e:
            self.assertIsInstance(e, ParseException)
            assert str(e) == expected_message

            if expected_cause:
                assert type(e.__cause__) == expected_cause
