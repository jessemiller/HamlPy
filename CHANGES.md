1.0a1 (TBD)
===================

* Refactor of parsing code giving ~40% performance improvement
* Added support for HTML style attribute dictionaries, e.g. %span(foo="bar")
* Fixed attribute values not being able to include braces (https://github.com/nyaruka/django-hamlpy/issues/39)
* Fixed attribute values which are Haml not being able to have blank lines (https://github.com/nyaruka/django-hamlpy/issues/41)
* Fixed sequential with tags ended up nested (https://github.com/nyaruka/django-hamlpy/issues/23) 
* Fixed templatize patching for Django 1.9+
* Changed support for ={..} style expressions (use #{..}) to be disabled by default (https://github.com/nyaruka/django-hamlpy/issues/16)
* Removed support for =# comment syntax which wasn't documented (use -#)
* Project now maintained by Nyaruka (https://github.com/nyaruka)

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
