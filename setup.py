from setuptools import setup, find_packages

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')  # noqa
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()  # noqa


def _is_requirement(line):
    """Returns whether the line is a valid package requirement."""
    line = line.strip()
    return line and not line.startswith("#")


def _read_requirements(filename):
    """Parses a file for pip installation requirements."""
    with open(filename) as requirements_file:
        contents = requirements_file.read()
    return [line.strip() for line in contents.splitlines() if _is_requirement(line)]


setup(
    name='django-hamlpy',
    version=__import__('hamlpy').__version__,
    description='Haml like syntax for Django templates.',
    long_description=read_md('README.md'),

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    keywords='haml django converter',
    url='http://github.com/nyaruka/django-hamlpy',
    license='MIT',

    maintainer='Nyaruka',
    maintainer_email='code@nyaruka.com',

    packages=find_packages(),
    install_requires=_read_requirements("requirements/base.txt"),
    tests_require=_read_requirements("requirements/tests.txt"),
    entry_points={
        'console_scripts': [
            'hamlpy-watcher = hamlpy.hamlpy_watcher:watch_folder'
        ]
    }
)
