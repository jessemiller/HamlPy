from __future__ import unicode_literals

# load templatize module to patch Django's templatize function
from . import templatize  # noqa

from .loaders import haml_loaders as _loaders

locals().update(_loaders)
