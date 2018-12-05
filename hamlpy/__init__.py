from django.apps import AppConfig

__version__ = '1.2'

HAML_EXTENSIONS = ('haml', 'hamlpy')


class Config(AppConfig):
    name = 'hamlpy'

    def ready(self):
        # patch Django's templatize method
        from .template import templatize  # noqa


default_app_config = 'hamlpy.Config'
