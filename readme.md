# HamlPy

HamlPy (pronounced "haml pie") is a tool for Django developers who want to use a Haml like syntax for their templates.
HamlPy is not a template engine in itself but simply a compiler which will convert HamlPy files into templates that Django can understand.


But wait, what is Haml?  Haml is an incredible template engine written in Ruby used a lot in the Rails community.  You can read more about it [here](http://www.haml-lang.com "Haml Home")

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
			%li.athelete= athelete.name

turns into..

	<ul id='atheletes'>
		{% for athelete in athelete_list %}
			<li class='athelete'>{{ athelete.name }}</li>
		{% endfor %}
	</ul>
	
## Reference

Check out the `reference.md` file for a complete reference and more examples.

## Status

HamlPy currently:

- has no configuration file.  which it should for a few reasons, like turning off what is autoescaped for example
- does not support some of the filters yet

## Contributing

Very happy to have contributions to this project. Please write tests for any new features and always ensure the current tests pass. You can run the tests from the hamlpy/test using nosetests by typing

    nosetests *.py
