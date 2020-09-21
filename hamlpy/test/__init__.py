import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "hamlpy.test.settings"
django.setup()
