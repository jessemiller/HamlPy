from __future__ import unicode_literals

import os

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loaders import filesystem, app_directories

from hamlpy import hamlpy
from hamlpy.template.utils import get_django_template_loaders

# Get options from Django settings
options_dict = {}

if hasattr(settings, 'HAMLPY_ATTR_WRAPPER'):
    options_dict.update(attr_wrapper=settings.HAMLPY_ATTR_WRAPPER)


def get_haml_loader(loader):
    if hasattr(loader, 'Loader'):
        BaseClass = loader.Loader
    else:
        class BaseClass(object):
            def load_template_source(self, *args, **kwargs):
                return loader.load_template_source(*args, **kwargs)

            def get_contents(self, origin):
                return loader.get_contents(origin)

    class Loader(BaseClass):
        def get_contents(self, origin):
            # Django>=1.9
            contents = super(Loader, self).get_contents(origin)
            name, _extension = os.path.splitext(origin.template_name)
            # os.path.splitext always returns a period at the start of extension
            extension = _extension.lstrip('.')

            if extension in hamlpy.VALID_EXTENSIONS:
                compiler = hamlpy.Compiler(options_dict=options_dict)
                return compiler.process(contents)

            return contents

        def load_template_source(self, template_name, *args, **kwargs):
            # Django<1.9
            name, _extension = os.path.splitext(template_name)
            # os.path.splitext always returns a period at the start of extension
            extension = _extension.lstrip('.')

            if extension in hamlpy.VALID_EXTENSIONS:
                try:
                    haml_source, template_path = super(Loader, self).load_template_source(
                        self._generate_template_name(name, extension), *args, **kwargs
                    )
                except TemplateDoesNotExist:
                    pass
                else:
                    hamlParser = hamlpy.Compiler(options_dict=options_dict)
                    html = hamlParser.process(haml_source)

                    return html, template_path

            raise TemplateDoesNotExist(template_name)

        load_template_source.is_usable = True

        def _generate_template_name(self, name, extension="hamlpy"):
            return "%s.%s" % (name, extension)

    return Loader


haml_loaders = dict((name, get_haml_loader(loader)) for (name, loader) in get_django_template_loaders())

HamlPyFilesystemLoader = get_haml_loader(filesystem)
HamlPyAppDirectoriesLoader = get_haml_loader(app_directories)
