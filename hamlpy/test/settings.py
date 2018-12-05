import django

from distutils.version import LooseVersion

DEBUG = True

DATABASES = {}

INSTALLED_APPS = ('hamlpy',)

TEMPLATE_DIR = 'hamlpy/test/templates'
TEMPLATE_LOADERS = [
    'hamlpy.template.loaders.HamlPyFilesystemLoader',
    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
]

if LooseVersion(django.get_version()) >= LooseVersion('1.8'):
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [TEMPLATE_DIR],
            'OPTIONS': {'loaders': TEMPLATE_LOADERS, 'debug': True}
        }
    ]
else:
    TEMPLATE_DIRS = [TEMPLATE_DIR]
    TEMPLATE_LOADERS = TEMPLATE_LOADERS
    TEMPLATE_DEBUG = True

SECRET_KEY = 'tots top secret'
