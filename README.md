Datacraft
=========
[![Build Status](https://circleci.com/gh/bbux-dev/datacraft/tree/develop.svg?style=svg)](https://circleci.com/gh/bbux-dev/datacraft/tree/main)
[![codecov](https://codecov.io/gh/bbux-dev/datacraft/branch/develop/graph/badge.svg?token=QFA9QZTQ05)](https://codecov.io/gh/bbux-dev/datacraft)

Overview
--------

This is a tool for making data according to specifications. The goal is to separate the structure of the data from 
the values that populate it. We do this by defining two core concepts: the Data Spec and the Field Spec. A Data Spec is
used to define all of the fields that should be generated for a record. The Data Spec does not care about the 
structure that the data will populate. A single Data Spec could be used to generate JSON, XML, or a csv file. Each 
field in the Data Spec has its own Field Spec that defines how the values for it should be created. There are a 
variety of core field types that are used to generate the data for each field. Where the built-in types are not 
sufficient, there is an easy way to create custom types and handlers for them using Custom Code Loading. The datacraft 
tool supports templating using the [Jinja2](https://pypi.org/project/Jinja2/) templating engine format.

Data is a key part of any application. Synthetic data can be used to test and exercise a system while it is under 
development or modification. By using a Data Spec to generate this synthetic data, it is more compact and easier to 
modify, update, and manage. It also lends itself to sharing and reuse. Instead of hosting large data files full of 
synthetic  test data, you can build Data Specs that encapsulate the information needed to generate the data. If 
well-designed, these can be easier to inspect and reason through compared with scanning thousands of lines of a csv 
file. `datacraft` makes it easy to generate millions or billions of records to use for development and testing of 
new or existing systems.

Docs
----

Find latest documentation and usage information here:
[datacraft.readthedocs.io](https://datacraft.readthedocs.io/en/latest/index.html)