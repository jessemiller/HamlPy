# Introduction

[![Build Status](https://travis-ci.org/nyaruka/django-hamlpy.svg?branch=master)](https://travis-ci.org/nyaruka/django-hamlpy)
[![Coverage Status](https://coveralls.io/repos/github/nyaruka/django-hamlpy/badge.svg?branch=master)](https://coveralls.io/github/nyaruka/django-hamlpy?branch=master)
[![PyPI Release](https://img.shields.io/pypi/v/django-hamlpy.svg)](https://pypi.python.org/pypi/django-hamlpy/)

Why type:

```html
<div class="left" id="banner">
    Greetings!
</div>
```

when you can just type:

```haml
.left#banner
    Greetings!
```

... and do something more fun with all the time you save not typing angle brackets and remembering to close tags? 

The syntax above is [Haml](http://www.haml-lang.com) - a templating language used extensively in the Ruby on Rails 
community. This library lets Django developers use a Haml like syntax in their templates. It's not a template engine in 
itself, but simply a compiler which will convert "HamlPy" files into templates that Django can understand.

This project is a fork of the no longer maintained [HamlPy](https://github.com/jessemiller/HamlPy). It introduces 
Python 3 support, support for new Django versions, and a host of new features and bug fixes. Note that the package name 
is now *django-hamlpy*.

## Installing

The latest stable version can be installed using [pip](http://pypi.python.org/pypi/pip/):

    pip install django-hamlpy

And the latest development version can be installed directly from GitHub:

    pip install git+https://github.com/nyaruka/django-hamlpy

**NOTE:** If you run into build errors, then you may need to install [python's development package](http://stackoverflow.com/a/21530768/2896976).

## Syntax

Almost all of the syntax of Haml is preserved.

```haml
#profile(style="width: 200px")
    .left.column
        #date 2010/02/18
        #address Toronto, ON
    .right.column<
        #bio Jesse Miller
```

turns into:

```htmldjango
<div id='profile' style="width: 200px">
    <div class='left column'>
        <div id='date'>2010/02/18</div>
        <div id='address'>Toronto, ON</div>
    </div>
    <div class='right column'><div id='bio'>Jesse Miller</div></div>
</div>
```

The main difference is instead of interpreting Ruby, or even Python we instead can create Django tags and variables. For 
example:

```haml
%ul#athletes
    - for athlete in athlete_list
        %li.athlete{'id': 'athlete_#{ athlete.pk }'}= athlete.name
```

becomes...

```htmldjango
<ul id='athletes'>
    {% for athlete in athlete_list %}
        <li class='athlete' id='athlete_{{ athlete.pk }}'>{{ athlete.name }}</li>
    {% endfor %}
</ul>
```

## Usage

There are two different ways to use this library.

### Option 1: Template loaders

These are Django template loaders which will convert any templates with `.haml` or `.hamlpy` extensions to regular 
Django templates whenever they are requested by a Django view. To use them, add them to the list of template loaders in 
your Django settings, e.g.

```python
TEMPLATES=[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./templates'],
        'OPTIONS': {
            'loaders': (
                'hamlpy.template.loaders.HamlPyFilesystemLoader',
                'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
                ...
            ), 
        }
    }
]
```

Ensure they are listed before the standard Django template loaders or these loaders will try to process your Haml 
templates.

#### Template caching

You can use these loaders with template caching - just add `django.template.loaders.cached.Loader` to your list of 
loaders, e.g.

```python
'loaders': (
    ('django.template.loaders.cached.Loader', (
        'hamlpy.template.loaders.HamlPyFilesystemLoader',
        'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
        ...
    )),
)
```

#### Settings

You can configure the Haml compiler with the following Django settings:

  * `HAMLPY_ATTR_WRAPPER` -- The character that should wrap element attributes. Defaults to `'` (an apostrophe).
  * `HAMLPY_DJANGO_INLINE_STYLE` -- Whether to support `={...}` syntax for inline variables in addition to `#{...}`. 
     Defaults to `False`.

### Option 2: Watcher

The library can also be used as a stand-alone program. There is a watcher script which will monitor Haml files in a 
given directory and convert them to HTML as they are edited.

```
usage: hamlpy_watcher.py [-h] [-v] [-i EXT [EXT ...]] [-ext EXT] [-r S]
                         [--tag TAG] [--attr-wrapper {",'}] [--django-inline]
                         [--jinja] [--once]
                         input_dir [output_dir]

positional arguments:
  input_dir             Folder to watch
  output_dir            Destination folder

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Display verbose output
  -i EXT [EXT ...], --input-extension EXT [EXT ...]
                        The file extensions to look for.
  -ext EXT, --extension EXT
                        The output file extension. Default is .html
  -r S, --refresh S     Refresh interval for files. Default is 3 seconds.
                        Ignored if the --once flag is set.
  --tag TAG             Add self closing tag. eg. --tag macro:endmacro
  --attr-wrapper {",'}  The character that should wrap element attributes.
                        This defaults to ' (an apostrophe).
  --django-inline       Whether to support ={...} syntax for inline variables
                        in addition to #{...}
  --jinja               Makes the necessary changes to be used with Jinja2.
  --once                Runs the compiler once and exits on completion.
                        Returns a non-zero exit code if there were any compile
                        errors.
```

### Create message files for translation

HamlPy must first be included in Django's list of apps, i.e.

```python
INSTALLED_APPS = [
  ...
  'hamlpy'
  ...
]
```

Then just include your Haml templates along with all the other files which contain translatable strings, e.g.

```bash
python manage.py makemessages --extension haml,html,py,txt
```

## Reference

Check out the [reference](http://github.com/nyaruka/django-hamlpy/blob/master/REFERENCE.md) file for the complete syntax 
reference and more examples.

## Class Based Views

This library also provides [the same class based generic views than django](https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-display/) with the enhancement that they start by looking for templates endings with `*.haml` and `*.hamlpy` in addition to their default templates. Apart from that, they are exactly the same class based generic views. For example:

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

The available view classes are:

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

All views are importable from `hamlpy.views.generic` and are built using the `HamlExtensionTemplateView` mixin which you 
can use to create your own custom Haml-using views. For example:

```python
from hamlpy.views.generic import HamlExtensionTemplateView

class MyNewView(HamlExtensionTemplateView, ParentViewType):
    pass
```

**Note**: `HamlExtensionTemplateView` *needs* to be first in the inheritance list.

## Contributing

We're always happy to have contributions to this project. To get started you'll need to clone the project and install 
the dependencies:

    virtualenv env
    source env/bin/activate
    pip install -r requirements/base.txt
    pip install -r requirements/tests.txt

Please write tests for any new features and always ensure the current tests pass. To run the tests, use:

    py.test hamlpy  
    
To run the performance test, use:

    python -m hamlpy.test.test_templates
