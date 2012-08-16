import os

from django.template import TemplateDoesNotExist
from django.template.loaders import filesystem, app_directories

from hamlpy import hamlpy

from djaml.utils import get_django_template_loaders


def get_haml_loader(loader):
    if hasattr(loader, 'Loader'):
        baseclass = loader.Loader
    else:
        class baseclass(object):
            def load_template_source(self, *args, **kwargs):
                return loader.load_template_source(*args, **kwargs)

    class Loader(baseclass):
        def load_template_source(self, template_name, *args, **kwargs):
            _name, _extension = os.path.splitext(template_name)

            for extension in ["hamlpy", "haml"]:
                try:
                    haml_source, template_path = super(Loader, self).load_template_source(
                        self._generate_template_name(_name, extension), *args, **kwargs
                    )
                except TemplateDoesNotExist:
                    pass
                else:
                    hamlParser = hamlpy.Compiler()
                    html = hamlParser.process(haml_source)

                    return html, template_path

            raise TemplateDoesNotExist(template_name)

        load_template_source.is_usable = True

        def _generate_template_name(self, name, extension="hamlpy"):
            return "%s.%s" % (name, extension)

    return Loader


haml_loaders = dict((name, get_haml_loader(loader))
        for (name, loader) in get_django_template_loaders())


DjamlFilesystemLoader = get_haml_loader(filesystem)
DjamlAppDirectoriesLoader = get_haml_loader(app_directories)
