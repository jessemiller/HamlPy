1.3 (2020-09-21)
================

* Add support for markdown extensions (https://github.com/nyaruka/django-hamlpy/pull/78)
* Drop support for Django 1.x, test on 2.x and 3.x

1.1.1 (2017-05-29)
===================

* Fix patching makemessages on Django 1.11

1.1 (2017-03-20)
===================

* Add support for more doc types (default is HTML5) (https://github.com/nyaruka/django-hamlpy/pull/63)
* Add format (html4/html5/xhtml) and escape_attrs (True/False) compiler options
* Don't use empty tag syntax or CDATA sections (can be overridden) in HTML5 format
* Fix patching of templatize for makemessages (https://github.com/nyaruka/django-hamlpy/pull/65)
* Add support for Django 1.11 betas (https://github.com/nyaruka/django-hamlpy/pull/62)
* Fix use of plural tag within blocktrans tag (https://github.com/nyaruka/django-hamlpy/pull/57)
* Add less, sass and escaped filters (https://github.com/nyaruka/django-hamlpy/pull/55)

1.0.1 (2017-01-26)
===================

* Add :preserve filter (https://github.com/nyaruka/django-hamlpy/pull/49)
* Fix filter lookup to ignore trailing whitespace

1.0 (2016-12-14)
===================

This is the first major release and there are some potentially breaking changes noted below.

* Refactor of parsing code giving ~40% performance improvement
* Added support for HTML style attribute dictionaries, e.g. `%span(foo="bar")`
* Improved error reporting from parser to help find problems in your templates
* Fixed attribute values not being able to include braces (https://github.com/nyaruka/django-hamlpy/issues/39)
* Fixed attribute values which are Haml not being able to have blank lines (https://github.com/nyaruka/django-hamlpy/issues/41)
* Fixed sequential `with` tags ended up nested (https://github.com/nyaruka/django-hamlpy/issues/23) 
* Fixed templatize patching for Django 1.9+
* Changed support for `={..}` style expressions to be disabled by default (https://github.com/nyaruka/django-hamlpy/issues/16)
* Removed support for `=#` comment syntax
* Project now maintained by Nyaruka (https://github.com/nyaruka)

Breaking Changes
----------------

* Support for `={...}` variable substitutions is deprecated and disabled by default, but can be enabled by setting 
  `HAMLPY_DJANGO_INLINE_STYLE` to `True` if you are using the template loaders, or specifying --django-inline if you are 
  using the watcher script. The preferred syntax for variable substitutions is `#{...}` as this is actual Haml and is 
  less likely conflict with other uses of the `=` character.
* The `=# ...` comment syntax is no longer supported. This is not Haml and was never documented anywhere. You should use 
  the `-# ...` syntax instead.
* Any line beginning with a colon is interpreted as a filter, so if this is not the case, you should escape the colon, 
  e.g. `\:not-a-filter `

0.86.1 (2016-11-15)
===================

* Fixed some incorrect relative imports #21 by @Kangaroux

0.86 (2016-11-11)
=================

* Add call and macro tags to the self-closing dict by @andreif
* Remove django 1.1 support by @rowanseymour
* Switch to a real parser instead of eval by @rowanseymour
* Improve tests and code quality by @rowanseymour
* Add performance tests by @rowanseymour
* Tag names can include a "-" (for angular for example) by @rowanseymour
* Don't uses tox anymore for testing by @rowanseymour
* Classes shorthand can come before a id one by @rowanseymour
* Added co-maintainership guidelines by @psycojoker

0.85 (2016-10-13)
=================

* Python 3 support by @rowanseymour https://github.com/Psycojoker/django-hamlpy/pull/1
* Attributes now output by alphabetic order (this was needed to have deterministic tests) by @rowanseymour https://github.com/Psycojoker/django-hamlpy/pull/2

0.84 (2016-09-25)
=================

* Add support for boolean attributes - see [Attributes without values (Boolean attributes)](http://github.com/psycojoker/django-hamlpy/blob/master/reference.md#attributes-without-values-boolean-attributes)
* Add Django class based generic views that looks for `*.haml` and `*.hamlpy` templates in additions of the normal ones (https://github.com/Psycojoker/django-hamlpy#class-based-generic-views)

0.83 (2016-09-23)
=================

* New fork since sadly hamlpy isn't maintained anymore
* Pypi release have been renamed "django-hamlpy" instead of "hamlpy"
* Added Django 1.9 compatibility (https://github.com/jessemiller/HamlPy/pull/166)
