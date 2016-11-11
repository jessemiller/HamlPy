from setuptools import setup, find_packages

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


def _is_requirement(line):
    """Returns whether the line is a valid package requirement."""
    line = line.strip()
    return line and not line.startswith("#")


def _read_requirements(filename):
    """Parses a file for pip installation requirements."""
    with open(filename) as requirements_file:
        contents = requirements_file.read()
    return [line.strip() for line in contents.splitlines() if _is_requirement(line)]


# Note to Jesse - only push sdist to PyPi, bdist seems to always break pip installer
setup(
    name='django-hamlpy',
    version='0.86',
    description='HAML like syntax for Django templates. Fork of unmaintained hamlpy.',
    long_description=read_md('readme.md'),

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    keywords='haml django converter',
    url='http://github.com/psycojoker/django-hamlpy',
    license='MIT',

    author='Jesse Miller',
    author_email='millerjesse@gmail.com',
    maintainer='Laurent Peuch',
    maintainer_email='cortex@worlddomination.be',

    packages=find_packages(),
    install_requires=_read_requirements("requirements/base.txt"),
    tests_require=_read_requirements("requirements/tests.txt"),
    entry_points={
        'console_scripts': [
            'hamlpy = hamlpy.hamlpy:convert_files',
            'hamlpy-watcher = hamlpy.hamlpy_watcher:watch_folder'
        ]
    }
)
