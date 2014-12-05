#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='est_upload',
    version='1.0.4',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    url='https://github.com/jneureuther/est_upload',
    license='CC BY-SA 4.0',
    author='Julian Neureuther',
    author_email='dev@jneureuther.de',
    description='Library to communicate with Exercise Submission Tool (https://est.informatik.uni-erlangen.de)',
    long_description=long_description,
    install_requires=['requests==2.3.0', 'python-magic', 'beautifulsoup4']
)
