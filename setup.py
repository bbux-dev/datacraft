# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    project_license = f.read()

setup(
    name='dataspec',
    version='0.1.0',
    description='Data Generation Utility',
    long_description=readme,
    author='Brian Buxton',
    author_email='bbux.dev@gmail.com',
    url='https://github.com/bbux-dev/dataspec',
    license=project_license,
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
