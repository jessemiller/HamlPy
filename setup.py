#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# vim: fenc=utf-8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
#

"""
File name: setup.py
Author: dhilipsiva <dhilipsiva@gmail.com>
Date created: 2015-12-13
"""

from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))
f = path.join(here, 'readme.md')

setup(
    name='HamlPy3',
    version='0.84.0',
    packages=['hamlpy', 'hamlpy.template'],
    author='dhilipsiva',
    author_email='dhilipsiva@gmail.com',
    description=(
        'A python 3 fork & drop-in replacement of HamlPy.'
        ' HAML like syntax for Django templates'
    ),
    keywords='haml django converter',
    url='http://github.com/appknox/HamlPy3',
    license='MIT',
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'hamlpy = hamlpy.hamlpy:convert_files',
            'hamlpy-watcher = hamlpy.hamlpy_watcher:watch_folder']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
