# HamlPy Reference

## Installing

	easy_install hamlpy
	
## Usage

To simply output the conversion to your console:

	hamlpy inputFile.haml
	
Or you can have it dump right into a file:

	hamlpy inputFile.haml outputFile.html
	
There is also a script which will watch for changed hamlpy extensions and regenerate the html as they are edited:

	hamlpy-watcher <watch-folder>
	
## Plain Text

Any line that is not interpreted as something else will be taken as plain text and outputted unmodified.  For example:

	%gee
		%whiz
			Wow this is cool!
			
is compiled to:

	<gee>
		<whiz>
			Wow this is cool!
		</whiz>
	</gee>

## Doctype

You can specify a specific doctype after the !!! The following doctypes are supported:

* `!!!`: XHTML 1.0 Transitional
* `!!! Strict`: XHTML 1.0 Strict
* `!!! Frameset`: XHTML 1.0 Frameset
* `!!! 5`: XHTML 5
* `!!! 1.1`: XHTML 1.1

## HTML Elements

### Element Name: %

The percent character placed at the beginning of the line will then be followed by the name of the element, then optionally modifiers (see below), a space, and text to be rendered inside the element.  It creates an element in the form of <element></element>.  For example:

	%one
		%two
			%three Hey there
			
is compiled to:

	<one>
		<two>
			<three>Hey there</three>
		</two>
	</one>

Any string is a valid element name and a opening and closing tag will automatically be generated.

### Attributes: {}

Brackets represent a Python dictionary that is used for specifying the attributes of an element.  The dictionary is placed after the tag is defined.  For example:

	%html{'xmlns':'http://www.w3.org/1999/xhtml', 'xml:lang':'en', 'lang':'en'}
	
is compiled to:

	<html xmlns='http://www.w3.org/1999/xhtml' xml:lang='en' lang='en'></html>

Long attribute dictionaries can be separated into multiple lines:

    %script{'type': 'text/javascript', 'charset': 'utf-8', 
            'href': '/long/url/to/javascript/resource.js'}

#### Attributes without values (Boolean attributes)

Attributes without values can be specified using Python's ```None``` keyword (without quotes). For example:

	%input{'type':'checkbox', value:'Test', checked: None}

is compiled to:

	<input type="checkbox" value="Test" checked />


#### 'class' and 'id' attributes

The 'class' and 'id' attributes can also be specified as a Python tuple whose elements will be joined together.  A 'class' tuple will be joined with " " and an 'id' tuple is joined with "_".  For example:

	%div{'id': ('article', '3'), 'class': ('newest', 'urgent')} Content
	
is compiled to:

	<div id='article_3' class='newest urgent'>Content</div>
	
### Class and ID: . and #

The period and pound sign are borrowed from CSS.  They are used as shortcuts to specify the class and id attributes of an element, respectively.  Multiple class names can be specified by chaining class names together with periods.  They are placed immediately after a tag and before an attribute dictionary.  For example:

	%div#things
		%span#rice Chicken Fried
		%p.beans{'food':'true'} The magical fruit
		%h1#id.class.otherclass La La La
	
is compiled to:

	<div id='things'>
		<span id='rice'>Chiken Fried</span>
		<p class='beans' food='true'>The magical fruit</p>
		<h1 id='id' class='class otherclass'>La La La</h1>
	</div>
	
And,

	%div#content
		%div.articles
			%div.article.title Doogie Howser Comes Out
			%div.article.date 2006-11-05
			%div.article.entry
				Neil Patrick Harris would like to dispel any rumors that he is straight
				
is compiled to:

	<div id='content'>
		<div class='articles'>
			<div class='article title'>Doogie Howser Comes Out</div>
			<div class='article date'>2006-11-05</div>
			<div class='article entry'>
				Neil Patrick Harris would like to dispel any rumors that he is straight
			</div>
		</div>
	</div>

These shortcuts can be combined with the attribute dictionary and they will be combined as if they were all put inside a tuple.  For example:

	%div#Article.article.entry{'id':'1', 'class':'visible'} Booyaka
	
is equivalent to:
	
	%div{'id':('Article','1'), 'class':('article','entry','visible')} Booyaka
	
and would compile to:

	<div id='Article_1' class='article entry visible'>Booyaka</div>
	
You can also use more pythonic array structures in the dictionary, like so:

    %div{'id':['Article','1'], 'class':['article','entry','visible']} Booyaka
	
#### Implicit div elements

Because divs are used so often, they are the default element.  If you only define a class and/or id using . or # the %div will be implied.  For example:

	#collection
		.item
			.description What a cool item!
			
will compile to:

	<div id='collection'>
		<div class='item'>
			<div class='description'>What a cool item!</div>
		</div>
	</div>
	
### Self-Closing Tags: /

The forward slash character, when placed at the end of a tag definition, causes the tag to be self-closed.  For example:

	%br/
	%meta{'http-equiv':'Content-Type', 'content':'text/html'}/
	
will compile to:

	<br />
	<meta http-quiv='Content-Type' content='text/html' />
	
Some tags are automatically closed, as long as they have no content.  `meta, img, link, script, br` and `hr` tags are automatically closed.  For example:

	%br
	%meta{'http-equiv':'Content-Type', 'content':'text/html'}
	
will compile to:

	<br />
	<meta http-quiv='Content-Type' content='text/html' />
	
## Comments

There are two types of comments supported.  Those that show up in the HTML and those that don't.

### HTML Comments /

The forward slash character, when placed at the beginning of a line, wraps all the text after it in an HTML comment.  For example:

	%peanutbutterjelly
		/ This is the peanutbutterjelly element
		I like sandwiches!
		
is compiled to:

	<peanutbutterjelly>
		<!-- This is the peanutbutterjelly element -->
		I like sandwiches!
	</peanutbutterjelly>
	
The forward slash can also wrap indented sections of code.  For example:

	/
		%p This doesn't render
		%div
			%h1 Because it's commented out!
			
is compiled to:

	<!--
		<p>This doesn't render</p>
		<div>
			<h1>Because it's commented out!</h1>
		</div>
	-->
	
### Conditional Comments /[]

You can use [Internet Explorer conditional comments](http://www.quirksmode.org/css/condcom.html) by enclosing the condition in square brackets after the /. For example:

    /[if IE]
        %h1 Get a better browser
    
is compiled to:

    <!--[if IE]>
        <h1>Get a better browser</h1>
    <![endif]-->
	
### HamlPy Comments: -#

The hyphen followed immediately by the pound sign signifies a silent comment.  Any text following this isn't rendered during compilation at all.  For example:

	%p foo
	-# Some comment
	%p bar
	
is compiled to:

	<p>foo</p>
	<p>bar</p>
	
## Django Specific Elements

The key difference in HamlPy from Haml is the support for Django elements.  The syntax for ruby evaluation is borrowed from Haml and instead outputs Django tags and variables.

### Django Variables: =

A line starting with an equal sign followed by a space and then content is evaluated as a Django variable.  For example:

	.article
		.preview
			= story.teaser
			
is compiled to:

	<div class='article'>
		<div class='preview'>
			{{ story.teaser }}
		</div>
	</div>
	
A Django variable can also be used as content for any HTML element by placing an equals sign as the last character before the space and content.  For example:

	%h2
		%a{'href':'stories/1'}= story.teaser
		
is compiled to:

	<h2>
		<a href='stories/1'>{{ story.teaser }}</a>
	</h2>

Variables can also be used in attributes, but only if the attribute contains nothing else other than that variable. For example:

	%a{'href':'= some_url'}

is compiled to:

	<a href='{{some_url}}'></a>
	
### Django Tags: -

The hypen character at the start of the line followed by a space and a Django tag will be inserted as a Django tag.  For example:

	- block content
		%h1= section.title
	
		- for dog in dog_list
			%h2
				= dog.name
	
is compiled to:

	{% block content %}
		<h1>{{ section.title }}</h1>
		
		{% for dog in dog_list %}
			<h2>
				{{ dog.name }}
			</h2>
		{% endfor %}
	{% endblock %}
	
	
Notice that block, for, if and else, as well as ifequal, ifnotequal, ifchanged and 'with' are all automatically closed.  Using endfor, endif, endifequal, endifnotequal, endifchanged or endblock will throw an exception.

## Filters

### :plain

Does not parse the filtered text. This is useful for large blocks of text without HTML tags, when you don’t want lines starting with . or - to be parsed.

### :javascript

Surrounds the filtered text with &lt;script&gt; and CDATA tags. Useful for including inline Javascript.

### :cdata

Surrounds the filtered text with CDATA tags.

### :css

Surrounds the filtered text with &lt;script&gt; and CDATA tags. Useful for including inline CSS.

### :highlight

This will output the filtered text with syntax highlighting using Pygments.

### :python

Execute the filtered text as python and outputs the result in the file. For example:

	for i in range(0, 5): print "<p>item %s</p>" % i
	
is compiled to:

	<p>item 0</p>
	<p>item 1</p>
	<p>item 2</p>
	<p>item 3</p>
	<p>item 4</p>

**Only one-line script are currently supported.**