# HamlPy

HamlPy (pronounced "haml pie") is a tool for Django developers who want to use a Haml like syntax for their templates.
HamlPy is not a template engine in itself but simply a compiler which will convert HamlPy files into templates that Django can understand.


But wait, what is Haml?  Haml is an incredible template engine written in Ruby used a lot in the Rails community.  You can read more about it [here](http://www.haml-lang.com "Haml Home").

## Installing

### Stable release

The latest stable version of HamlPy can be installed using [setuptools](http://pypi.python.org/pypi/setuptools/) `easy_install hamlpy` or  [pip](http://pypi.python.org/pypi/pip/) (`pip install hamlpy`)

### Development

The latest development version can be installed directly from GitHub:

    pip install https://github.com/jessemiller/HamlPy/tarball/master

## Syntax

Almost all of the XHTML syntax of Haml is preserved.  

	#profile
		.left.column
			#date 2010/02/18
			#address Toronto, ON
		.right.column
			#bio Jesse Miller
			
turns into..

	<div id='profile'>
		<div class='left column'>
			<div id='date'>2010/02/18</div>
			<div id='address'>Toronto, ON</div>
		</div>
		<div class='right column'>
			<div id='bio'>Jesse Miller</div>
		</div>
	</div>
	

The main difference is instead of interpreting Ruby, or even Python we instead can create Django Tags and Variables

	%ul#atheletes
		- for athelete in athelete_list
			%li.athelete{'id': 'athelete_{{ athelete.pk }}'}= athelete.name

turns into..

	<ul id='atheletes'>
		{% for athelete in athelete_list %}
			<li class='athelete' id='athelete_{{ athelete.pk }}'>{{ athelete.name }}</li>
		{% endfor %}
	</ul>

## Usage

To simply output the conversion to your console:

	hamlpy inputFile.haml
	
Or you can have it dump right into a file:

	hamlpy inputFile.haml outputFile.html
	
There is also a script which will watch for changed hamlpy extensions and regenerate the html as they are edited:

	hamlpy-watcher <watch-folder> [destination_folder]
	
## Reference

Check out the [reference.md](http://github.com/jessemiller/HamlPy/blob/master/reference.md "HamlPy Reference") file for a complete reference and more examples.

## Status

HamlPy currently:

- has no configuration file.  which it should for a few reasons, like turning off what is autoescaped for example
- does not support some of the filters yet

## Contributing

Very happy to have contributions to this project. Please write tests for any new features and always ensure the current tests pass. You can run the tests from the hamlpy/test using nosetests by typing

    nosetests *.py
