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

	%ul#athletes
		- for athlete in athlete_list
			%li.athlete{'id': 'athlete_{{ athlete.pk }}'}= athlete.name

turns into..

	<ul id='athletes'>
		{% for athlete in athlete_list %}
			<li class='athlete' id='athlete_{{ athlete.pk }}'>{{ athlete.name }}</li>
		{% endfor %}
	</ul>

## Usage

### Option 1: Template loader

The template loader was originally written by [Chris Hartjes](https://github.com/chartjes) under the name 'djaml'. This project has now been merged into the HamlPy codebase.

Add the HamlPy template loaders to the Django template loaders:

    TEMPLATE_LOADERS = (
	    'hamlpy.template.loaders.HamlPyFilesystemLoader',
	    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',   
        ...
    )

If you don't put the HamlPy template loader first, then the standard Django template loaders will try to process
it first. Make sure your templates have a `.haml` or `.hamlpy` extension, and put them wherever you've told Django
to expect to find templates (TEMPLATE_DIRS).

#### Template caching

For caching, just add `django.template.loaders.cached.Loader` to your TEMPLATE_LOADERS:

	TEMPLATE_LOADERS = (
	    ('django.template.loaders.cached.Loader', (
		    'hamlpy.template.loaders.HamlPyFilesystemLoader',
		    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
		    ...
	    )),   
	)

#### Settings

Following values in Django settings affect haml processing:

  * `HAMLPY_ATTR_WRAPPER` -- The character that should wrap element attributes. This defaults to ' (an apostrophe).

### Option 2: Watcher 

HamlPy can also be used as a stand-alone program. There is a script which will watch for changed hamlpy extensions and regenerate the html as they are edited:


        usage: hamlpy-watcher [-h] [-v] [-i EXT [EXT ...]] [-ext EXT] [-r S]
                            [--tag TAG] [--attr-wrapper {",'}]
                            input_dir [output_dir]

        positional arguments:
        input_dir             Folder to watch
        output_dir            Destination folder

        optional arguments:
        -h, --help            show this help message and exit
        -v, --verbose         Display verbose output
        -i EXT [EXT ...], --input-extension EXT [EXT ...]
                                The file extensions to look for
        -ext EXT, --extension EXT
                                The output file extension. Default is .html
        -r S, --refresh S     Refresh interval for files. Default is 3 seconds
        --tag TAG             Add self closing tag. eg. --tag macro:endmacro
        --attr-wrapper {",'}  The character that should wrap element attributes.
                                This defaults to ' (an apostrophe).
        --jinja               Makes the necessary changes to be used with Jinja2

Or to simply convert a file and output the result to your console:

	hamlpy inputFile.haml
	
Or you can have it dump to a file:

	hamlpy inputFile.haml outputFile.html

Optionally, `--attr-wrapper` can be specified:

    hamlpy inputFile.haml --attr-wrapper='"'

Using the `--jinja` compatibility option adds macro and call tags, and changes the `empty` node in the `for` tag to `else`.

For HamlPy developers, the `-d` switch can be used with `hamlpy` to debug the internal tree structure.
	
### Create message files for translation

There is a very simple solution.

	django-admin.py makemessages --settings=<project.settings> -a
	
Where:

  * project.settings -- Django configuration file where  module "hamlpy" is configured properly.
	
## Reference

Check out the [reference.md](http://github.com/jessemiller/HamlPy/blob/master/reference.md "HamlPy Reference") file for a complete reference and more examples.

## Status

HamlPy currently:

- has no configuration file.  which it should for a few reasons, like turning off what is autoescaped for example
- does not support some of the filters yet

## Contributing

Very happy to have contributions to this project. Please write tests for any new features and always ensure the current tests pass. You can run the tests from the **hamlpy/test** folder using nosetests by typing

    nosetests *.py
