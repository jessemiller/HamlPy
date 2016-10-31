from __future__ import unicode_literals

import imp
from os import listdir
from os.path import dirname, splitext

try:
  from django.template import loaders
  _django_available = True
except ImportError as e:
  _django_available = False

MODULE_EXTENSIONS = tuple([suffix[0] for suffix in imp.get_suffixes()])

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
    package_path = dirname(loaders.__file__)
    contents = set([splitext(module)[0]
            for module in listdir(package_path)
            if module.endswith(MODULE_EXTENSIONS)])
    return contents
