# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='datamaker',
    version='0.1.0',
    description='Data Generation Utility',
    long_description=readme,
    author='Brian Buxton',
    author_email='bbux.aws@gmail.com',
    url='https://github.com/bbux-aws/datamaker',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
