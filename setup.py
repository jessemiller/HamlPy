from setuptools import setup

# Note to Jesse - only push sdist to PyPi, bdist seems to always break pip installer
setup(name='hamlpy',
      version = '0.80.4',
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
