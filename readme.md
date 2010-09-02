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
	

The main difference is instead of interpretting Ruby, or even Python we instead can create Django Tags and Variables

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

Check out the [reference.md](http://github.com/jessemiller/HamlPy/blob/master/reference.md "HamlPy Reference") for a complete reference and more examples.

## Status

HamlPy currently cannot:

- Do variable interpolation.  So there is currently no way to go `%p This is some cool #{coolThing.text}`.

