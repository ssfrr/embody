#!/usr/bin/env python

from setuptools import setup

setup(
    name='embody',
    version='0.0.1',
    description='Tools for embedded C project',
    packages=['embody'],
    scripts=['bin/embody'],
    author='Spencer Russell',
    author_email='sfr@media.mit.edu',
    license='MIT',
    install_requires=[
        'jinja2',
        'docopt',
        'pycparser',
    ]
)
