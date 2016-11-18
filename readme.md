# Introduction

[![Build Status](https://travis-ci.org/Psycojoker/django-hamlpy.svg?branch=master)](https://travis-ci.org/Psycojoker/django-hamlpy)
[![Coverage Status](https://coveralls.io/repos/github/Psycojoker/django-hamlpy/badge.svg?branch=master)](https://coveralls.io/github/Psycojoker/django-hamlpy?branch=master)

This is a tool for Django developers who want to use a Haml like syntax in their templates. It is not a template engine 
in itself, but simply a compiler which will convert HamlPy files into templates that Django can understand.

Haml is an incredible template language written in Ruby used extensively in the Rails community. You can read more about 
it [here](http://www.haml-lang.com "Haml Home").

This project is a fork of the no longer maintained [HamlPy](https://github.com/jessemiller/HamlPy), and wouldn't exist 
without all of hard work by Jesse Miller and others, for which we're very grateful.

The major new changes and features are:

* The PyPI package has been renamed to *django-hamlpy*
* Support for Django 1.9+
* Support for Python 2.7 and 3.4+
* [Boolean attribute](http://github.com/psycojoker/django-hamlpy/blob/master/reference.md#attributes-without-values-boolean-attributes) syntax is supported
* Includes Django [class based generic views](https://github.com/Psycojoker/django-hamlpy#class-based-generic-views) that look for `*.haml` and `*.hamlpy` templates.

## Installing

The latest stable version can be installed using [pip](http://pypi.python.org/pypi/pip/):

    pip install django-hamlpy

The latest development version can be installed directly from GitHub:

    pip install git+https://github.com/psycojoker/django-hamlpy

**NOTE:** If you are using Linux, you may need to install [python's development package](http://stackoverflow.com/a/21530768/2896976) if you are encountering build errors.

## Syntax

Almost all of the XHTML syntax of Haml is preserved.

```haml
#profile
    .left.column
        #date 2010/02/18
        #address Toronto, ON
    .right.column
        #bio Jesse Miller
```

turns into:

```htmldjango
<div id='profile'>
    <div class='left column'>
        <div id='date'>2010/02/18</div>
        <div id='address'>Toronto, ON</div>
    </div>
    <div class='right column'>
        <div id='bio'>Jesse Miller</div>
    </div>
</div>
```


The main difference is instead of interpreting Ruby, or even Python we instead can create Django Tags and Variables

```haml
%ul#athletes
    - for athlete in athlete_list
        %li.athlete{'id': 'athlete_{{ athlete.pk }}'}= athlete.name
```

turns into..

```htmldjango
<ul id='athletes'>
    {% for athlete in athlete_list %}
        <li class='athlete' id='athlete_{{ athlete.pk }}'>{{ athlete.name }}</li>
    {% endfor %}
</ul>
```

## Usage

### Option 1: Template loader

The template loader was originally written by [Chris Hartjes](https://github.com/chartjes) under the name 'djaml'. This project has now been merged into the django-hamlpy codebase.

Add the django-hamlpy template loaders to the Django template loaders:

```python
TEMPLATE_LOADERS = (
    'hamlpy.template.loaders.HamlPyFilesystemLoader',
    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
    ...
)
```

If you don't put the django-hamlpy template loader first, then the standard Django template loaders will try to process
it first. Make sure your templates have a `.haml` or `.hamlpy` extension, and put them wherever you've told Django
to expect to find templates (TEMPLATE_DIRS).

#### Template caching

For caching, just add `django.template.loaders.cached.Loader` to your TEMPLATE_LOADERS:

```python
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'hamlpy.template.loaders.HamlPyFilesystemLoader',
        'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
        ...
    )),
)
```

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

```bash
hamlpy inputFile.haml
```

Or you can have it dump to a file:

```bash
hamlpy inputFile.haml outputFile.html
```

Optionally, `--attr-wrapper` can be specified:

```bash
hamlpy inputFile.haml --attr-wrapper='"'
```

Using the `--jinja` compatibility option adds macro and call tags, and changes the `empty` node in the `for` tag to `else`.

For HamlPy developers, the `-d` switch can be used with `hamlpy` to debug the internal tree structure.

### Create message files for translation

There is a very simple solution.

```bash
django-admin.py makemessages --settings=<project.settings> -a --extension haml,html,py,txt
```

Where:

  * project.settings -- Django configuration file where  module "hamlpy" is configured properly.

## Reference

Check out the [reference.md](http://github.com/psycojoker/django-hamlpy/blob/master/reference.md "HamlPy Reference") file for a complete reference and more examples.

## Class Based Generic Views

django-hamlpy provides [the same class based generic views than django](https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-display/) with the enhancement that they start by looking for templates endings with `*.haml` and `*.hamlpy` in additions to their default templates. Appart from that they are exactly the same class based generic views.

Example:

```python
from hamlpy.views.generic import DetailView, ListView
from my_app.models import SomeModel

# will look for the templates `my_app/somemodel_detail.haml`,
# `my_app/somemodel_detail.hamlpy` and  `my_app/somemodel_detail.html`
DetailView.as_view(model=SomeModel)

# will look for the templates `my_app/somemodel_list.haml`,
# `my_app/somemodel_list.hamlpy` and  `my_app/somemodel_list.html`
ListView.as_view(model=SomeModel)
```

The available generic views are:

Display views:

* [DetailView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#detailview)
* [ListView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#listview)

Edit views:

* [CreateView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#createview)
* [UpdateView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#updateview)
* [DeleteView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#deleteview)

Date related views:

* [DateDetailView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#datedetailview)
* [ArchiveIndexView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#archiveindexview)
* [YearArchiveView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#yeararchiveview)
* [MonthArchiveView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#montharchiveview)
* [WeekArchiveView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#weekarchiveview)
* [DayArchiveView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#dayarchiveview)
* [TodayArchiveView](https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-display/#todayarchiveview)

All views are importable from `hamlpy.views.generic` so you just need to switch
`django` to `hamlpy` in your files to benefit from them.

### Uses HamlExtensionTemplateView to create similar views

All those views are built using `HamlExtensionTemplateView` mixin. It calls
[get_template_names](https://docs.djangoproject.com/en/1.10/ref/class-based-views/mixins-simple/#django.views.generic.base.TemplateResponseMixin.get_template_names) from its super classes, looks for all template names
endings with `.html`, `.htm` and `.xml` and had at the beginning of this list
of templates name the same template base names but with the `.haml` and
`.hamlpy` extensions.

Example usage:

```python
from hamlpy.views.generic import HamlExtensionTemplateView

class MyNewView(HamlExtensionTemplateView, ParentViewWithAGetTemplateNames):
    pass
```

`HamlExtensionTemplateView` *needs* to be first in the inheritance list.

## Status

HamlPy currently:

- has no configuration file, which it should for a few reasons, like turning off what is autoescaped for example
- does not support some of the filters yet

## Contributing

Very happy to have contributions to this project and new co-maintainers. To get started you'll need to clone the
project and install the dependencies:

    virtualenv env
    source env/bin/activate
    pip install -r requirements/base.txt
    pip install -r requirements/tests.txt

Please write tests for any new features and always ensure the current tests pass. To run the tests, use:

    py.test hamlpy  
    
To run the performance test, use:

    python -m hamlpy.test.test_templates
