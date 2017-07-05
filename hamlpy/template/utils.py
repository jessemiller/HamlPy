from os.path import dirname
from pkgutil import iter_modules

try:
  from django.template import loaders
  _django_available = True
except ImportError, e:
  _django_available = False

def get_django_template_loaders():
    if not _django_available:
        return []
    return [(loader.__name__.rsplit('.',1)[1], loader)
                for loader in get_submodules(loaders)
                if hasattr(loader, 'Loader')]

def get_submodules(package):
    submodules = ("%s.%s" % (package.__name__, module)
                for module in package_contents(package))
    return [__import__(module, {}, {}, [module.rsplit(".", 1)[-1]])
                for module in submodules]

def package_contents(package):
    package_path = dirname(package.__file__)
    return set([name for (ldr, name, ispkg) in iter_modules([package_path])])
