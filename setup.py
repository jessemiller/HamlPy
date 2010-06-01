from setuptools import setup

setup(name='hamlpy',
      version = '0.1b1',
      packages = ['hamlpy'],
      author = 'Jesse Miller',
      author_email = 'millerjesse@gmail.com',
      description = 'HAML like syntax for Django templates',
      keywords = 'haml django converter',
      url = 'http://github.com/jessemiller/HamlPy',
      
      entry_points = {
          'console_scripts' : ['hamlpy = hamlpy.hamlpy:convert_files']
      }
    )