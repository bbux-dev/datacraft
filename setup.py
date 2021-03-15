# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages


def _read_files_to_string(*filenames):
    strings = []
    for filename in filenames:
        with open(filename) as f:
            strings.append(f.read())
    return '\n\n'.join(strings)


def long_description():
    return _read_files_to_string('README.md')


def project_license():
    return _read_files_to_string('LICENSE')


def requires():
    with open('requirements.txt') as f:
        lines = f.readlines()
        return [line.strip() for line in lines]


def version():
    with open('dataspec/__init__.py') as f:
        match = re.search(r"__version__ = '([\d\.]+)'", f.read())
        return match.group(1)


setup(
    name='dataspec',
    version=version(),
    description='Data Generation Through Specification',
    long_description=long_description(),
    author='Brian Buxton',
    author_email='bbux.dev@gmail.com',
    url='https://github.com/bbux-dev/dataspec',
    license='MIT',
    packages=find_packages(),
    keywords=['data', 'synthetic', 'generator', 'specification', 'spec', 'data spec'],
    install_requires=requires(),
    scripts=['bin/dataspec'],
    package_data={
        "dataspec": ["schema/*.schema.json", "schema/definitions.json"]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
