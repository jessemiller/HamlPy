import os

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loaders import filesystem, app_directories

from hamlpy import HAML_EXTENSIONS
from hamlpy.compiler import Compiler
from hamlpy.template.utils import get_django_template_loaders

# Get options from Django settings
options = {}

if hasattr(settings, 'HAMLPY_ATTR_WRAPPER'):
    options.update(attr_wrapper=settings.HAMLPY_ATTR_WRAPPER)

if hasattr(settings, 'HAMLPY_DJANGO_INLINE_STYLE'):
    options.update(django_inline_style=settings.HAMLPY_DJANGO_INLINE_STYLE)


def get_haml_loader(loader):
    class Loader(loader.Loader):
        def get_contents(self, origin):
            # Django>=1.9
            contents = super(Loader, self).get_contents(origin)
            name, _extension = os.path.splitext(origin.template_name)
            # os.path.splitext always returns a period at the start of extension
            extension = _extension.lstrip('.')

            if extension in HAML_EXTENSIONS:
                compiler = Compiler(options=options)
                return compiler.process(contents)

            return contents

        def load_template_source(self, template_name, *args, **kwargs):
            # Django<1.9
            name, _extension = os.path.splitext(template_name)
            # os.path.splitext always returns a period at the start of extension
            extension = _extension.lstrip('.')

            if extension in HAML_EXTENSIONS:
                try:
                    haml_source, template_path = super(Loader, self).load_template_source(
                        self._generate_template_name(name, extension), *args, **kwargs
                    )
                except TemplateDoesNotExist:  # pragma: no cover
                    pass
                else:
                    compiler = Compiler(options=options)
                    html = compiler.process(haml_source)

                    return html, template_path

            raise TemplateDoesNotExist(template_name)

        load_template_source.is_usable = True

        @staticmethod
        def _generate_template_name(name, extension="hamlpy"):
            return "%s.%s" % (name, extension)

    return Loader


haml_loaders = dict((name, get_haml_loader(loader)) for (name, loader) in get_django_template_loaders())

HamlPyFilesystemLoader = get_haml_loader(filesystem)
HamlPyAppDirectoriesLoader = get_haml_loader(app_directories)
