0.86 (unreleased)
=================

* add call and macro tags to the self-closing dict by @andreif

0.85 (2016-10-13)
=================

* python3 support by @rowanseymour https://github.com/Psycojoker/django-hamlpy/pull/1
* tags attributes are ouputed by alphabetic order (this was needed to have deterministic tests) by @rowanseymour https://github.com/Psycojoker/django-hamlpy/pull/2

0.84 (2016-09-25)
=================

* single variables syntax is allowed in haml dict for single variables see [Attributes without values (Boolean attributes)](http://github.com/psycojoker/django-hamlpy/blob/master/reference.md#attributes-without-values-boolean-attributes)
* ship with a version of django class based generic views that looks for `*.haml` and `*.hamlpy` templates in additions of the classcal ones. https://github.com/Psycojoker/django-hamlpy#class-based-generic-views

0.83 (2016-09-23)
=================

* fork since sadly hamlpy isn't maintained anymore
* the pypi release have been renamed "django-hamlpy" instead of "hamlpy"
* compatible with django>=1.9 thanks to https://github.com/jessemiller/HamlPy/pull/166
You might also be interested in [hamlpy3](hamlpy3) which is a python 3 **only**
