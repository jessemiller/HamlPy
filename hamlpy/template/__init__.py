from .loaders import haml_loaders as _loaders
from django.utils import translation

from .templatize import patch_templatize

locals().update(_loaders)

translation.templatize = patch_templatize(translation.templatize)
