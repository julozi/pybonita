# -*- coding: utf-8 -*-
#!/usr/bin/env python
from setuptools import setup

setup(
    name='pybonita',
    version='0.1',
    author='Tony Moutaux, Julien Seiler',
    author_email='julien.seiler@gmail.com, moutaux@igbmc.fr',
    packages=['pybonita'],
    description='pybonita is a Python wrapper for the Bonita REST API',
    long_description='',
    license='BSD License',
    platforms='any',
    install_requires=['requests','lxml','beautifulsoup4'],
    tests_require='nose',
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
