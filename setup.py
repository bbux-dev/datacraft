# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    project_license = f.read()

with open('requirements.txt') as f:
    lines = f.readlines()
    requires = [line.strip() for line in lines]

setup(
    name='dataspec',
    version='0.1.0',
    description='Data Generation Through Specification',
    long_description=readme,
    author='Brian Buxton',
    author_email='bbux.dev@gmail.com',
    url='https://github.com/bbux-dev/dataspec',
    license=project_license,
    packages=find_packages(),
    keywords=['data', 'synthetic', 'generator', 'specification', 'spec', 'data spec'],
    install_requires=requires,
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
    ],
)
