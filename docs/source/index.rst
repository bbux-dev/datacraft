Welcome to Datacraft's documentation!
=====================================

**Datacraft**

Check out the :doc:`usage` section for further information, including
how to :ref:`install<installation>` the project.

Overview
========

Datacraft is a tool for generating synthetic data. We do this by providing a JSON based domain specific language (DSL)
for specifying the fields present in a record apart from what form the record takes. The goal is to separate the
structure of the data from the values that populate it. We do this by defining two core concepts: the Data Spec and
the Field Spec. A Data Spec is used to define all of the fields that should be generated for a record. The Data Spec
does not care about the structure of the records it will populate. A single Data Spec could be used to generate JSON,
XML, a csv file, or rows in a Database. Each field in the Data Spec is described by a Field Spec. A Field Spec
defines how the values for a field should be generated. There are a variety of built-in field types that can be used
to describe the data structure and format for fields. Where the built-in types are not sufficient, there is an easy way
to create custom types and handlers for them using :ref:`Custom Code<custom_code>` Loading. The ``datacraft`` tool
supports templating using the `Jinja2 <https://pypi.org/project/Jinja2/>`_ templating engine format.

Data is a key part of any application. Synthetic data can be used to test and exercise a system while it is under
development or modification. By using a Data Spec to generate this synthetic data, it is more compact and easier to
modify, update, and manage. It also lends itself to sharing and reuse. Instead of hosting large data files full of
synthetic  test data, you can build Data Specs that encapsulate the information needed to generate the data. If
well-designed, these can be easier to inspect and reason through compared with scanning thousands of lines of a csv
file. It is also easy to generate millions or billions of records to use for development and testing of new or
existing systems.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    usage
    fieldspecs
    coretypes
    examples
    cli
    api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`