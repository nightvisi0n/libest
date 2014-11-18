#!/usr/bin/env python

from distutils.core import setup

setup(
    name='est_upload',
    version='1.0.0',
    packages=[''],
    url='https://github.com/jneureuther/est_upload',
    license='CC BY-SA 4.0',
    author='Julian Neureuther',
    author_email='dev@jneureuther.de',
    description='Library to communicate with Exercise Submission Tool (https://est.informatik.uni-erlangen.de)',
    install_requires=['requests', 'python-magic', 'beautifulsoup4']
)
