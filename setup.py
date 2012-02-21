from setuptools import setup

setup(name='hamlpy',
      version = '0.7',
      download_url = 'git@github.com:jessemiller/HamlPy.git',
      packages = ['hamlpy'],
      author = 'Jesse Miller',
      author_email = 'millerjesse@gmail.com',
      description = 'HAML like syntax for Django templates',
      keywords = 'haml django converter',
      url = 'http://github.com/jessemiller/HamlPy',
      license = 'MIT',
      requires = [
        'django',
        'pygments'
      ],
      entry_points = {
          'console_scripts' : ['hamlpy = hamlpy.hamlpy:convert_files',
                               'hamlpy-watcher = hamlpy.hamlpy_watcher:watch_folder']
      }
    )
