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
	
