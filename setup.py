# -*- coding: utf-8 -*-

# Modified version of: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='dpm86xx',
    version='0.1.3',
    description='Python package to control Joy-IT DPM86XX power supplys.',
    long_description=readme,
    author='biozoom services GmbH',
    author_email='stern@biozoom.net',
    url='https://biozoom.net/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
