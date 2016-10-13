from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


# Note to Jesse - only push sdist to PyPi, bdist seems to always break pip installer
setup(
    name='django-hamlpy',
    version='0.85',
    packages=['hamlpy', 'hamlpy.template', 'hamlpy.views', 'hamlpy.views.generic'],
    author='Jesse Miller',
    author_email='millerjesse@gmail.com',
    maintainer='Laurent Peuch',
    maintainer_email='cortex@worlddomination.be',
    description='HAML like syntax for Django templates. Fork of unmainted hamlpy.',
    long_description=read_md('readme.md'),
    keywords='haml django converter',
    url='http://github.com/psycojoker/django-hamlpy',
    license='MIT',
    test_suite='hamlpy.test',
    install_requires=['six'],
    setup_requires=['mock'],
    entry_points={
        'console_scripts':
            ['hamlpy = hamlpy.hamlpy:convert_files',
             'hamlpy-watcher = hamlpy.hamlpy_watcher:watch_folder']
    }
)
