from setuptools import setup

# Note to Jesse - only push sdist to PyPi, bdist seems to always break pip installer
setup(
    name='django-hamlpy',
    version='0.83',
    download_url='git@github.com:jessemiller/HamlPy.git',
    packages=['hamlpy', 'hamlpy.template'],
    author='Jesse Miller',
    author_email='millerjesse@gmail.com',
    description='HAML like syntax for Django templates',
    keywords='haml django converter',
    url='http://github.com/psycojoker/django-hamlpy',
    license='MIT',
    test_suite='hamlpy.test',
    install_requires=[],
    setup_requires=['mock'],
    entry_points={
        'console_scripts':
            ['hamlpy = hamlpy.hamlpy:convert_files',
             'hamlpy-watcher = hamlpy.hamlpy_watcher:watch_folder']
    }
)
