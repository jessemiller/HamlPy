# HamlPy Reference

## Installing

	easy_install hamlpy
	
## Usage

To simply output the conversion to your console:

	hamlpy inputFile.hamlpy
	
Or you can have it dump right into a file:

	hamlpy inputFile.hamlpy outputFile.html
	
## A note about output

All of the following examples will show the HTML output nicely formatted.  Currently HamlPy actually outputs it with all white space stripped but the examples are formatted this way just for easy reading. 

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

