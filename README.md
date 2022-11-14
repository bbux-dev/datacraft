Datacraft
=========


[![Build Status](https://circleci.com/gh/bbux-dev/datacraft/tree/develop.svg?style=shield)](https://circleci.com/gh/bbux-dev/datacraft/tree/main)
[![codecov](https://codecov.io/gh/bbux-dev/datacraft/branch/develop/graph/badge.svg?token=QFA9QZTQ05)](https://codecov.io/gh/bbux-dev/datacraft)

A tool for generating synthetic data.

Overview
--------

Datacraft is a tool for generating synthetic data. We do this by providing a JSON based domain specific language 
(DSL) for specifying the fields present in a record apart from what form the record takes. The goal is to separate 
the structure of the data from the values that populate it. We do this by defining two core concepts: the Data Spec 
and the Field Spec. A Data Spec is used to define all the fields that should be generated for a record. The Data 
Spec does not care about the structure of the records it will populate. A single Data Spec could be used to generate
JSON, XML, a csv file, or rows in a Database. Each field in the Data Spec is described by a Field Spec. A Field Spec 
defines how the values for a field should be generated. There are a variety of built-in field types that can be used 
to describe the data structure and format for fields. Where the built-in types are not sufficient, there is an easy 
way to create custom types and handlers for them using
[Custom Code Loading](https://datacraft.readthedocs.io/en/develop/usage.html#custom-code). The `datacraft` tool 
supports templating using the [Jinja2](https://pypi.org/project/Jinja2/) templating engine format.

Data is a key part of any application. Synthetic data can be used to test and exercise a system while it is under 
development or modification. By using a Data Spec to generate this synthetic data, it is more compact and easier to 
modify, update, and manage. It also lends itself to sharing and reuse. Instead of hosting large data files full of 
synthetic test data, you can build Data Specs that encapsulate the information needed to generate the data. If 
well-designed, these can be easier to inspect and reason through compared with scanning thousands of lines of a csv 
file. `datacraft` makes it easy to generate millions or billions of records to use for development and testing of 
new or existing systems. Datacraft also has a python API so that you can generate your synthetic data as part of your
test suite or application without have to use online tools or external services.

Docs
----

Find the latest documentation and detailed usage information here:
[datacraft.readthedocs.io](https://datacraft.readthedocs.io/en/latest/index.html)

Installation
------------

```shell
$ pip install datacraft

$ datacraft -h # for full command line usage
```

Basic Usage
-----------

### Command Line

```shell
$ datacraft type-list # list all available field spec types ...
```

```shell
$ datacraft --type-help combine
INFO [05-Jun-2050 05:52:59 PM] Starting Loading Configurations...
INFO [05-Jun-2050 05:52:59 PM] Loading custom type loader: core
INFO [05-Jun-2050 05:52:59 PM] Loading custom type loader: xeger
-------------------------------------
combine | Example Spec:
{
  "name": {
    "type": "combine",
    "refs": ["first", "last"],
    "config": {
      "join_with": " "
    }
  },
  "refs": {
    "first": {
      "type": "values",
      "data": ["zebra", "hedgehog", "llama", "flamingo"]
    },
    "last": {
      "type": "values",
      "data": ["jones", "smith", "williams"]
    }
  }
}
datacraft -s spec.json -i 3 --format json -x -l off
[{"name": "zebra jones"}, {"name": "hedgehog smith"}, {"name": "llama williams"}]
```

### Python API

```python
import datacraft

spec = {
    "id": {"type": "uuid"},
    "timestamp": {"type": "date.iso.millis"},
    "handle": {"type": "cc-word", "config": { "min": 4, "max": 8, "prefix": "@" } }
}

print(*datacraft.entries(spec, 3), sep='\n')
```

```python
{'id': '40bf8be1-23d2-4e93-9b8b-b37103c4b18c', 'timestamp': '2050-12-03T20:40:03.709', 'handle': '@WPNn'}
{'id': '3bb5789e-10d1-4ae3-ae61-e0682dad8ecf', 'timestamp': '2050-11-20T02:57:48.131', 'handle': '@kl1KUdtT'}
{'id': '474a439a-8582-46a2-84d6-58bfbfa10bca', 'timestamp': '2050-11-29T18:08:44.971', 'handle': '@XDvquPI'}
```

Type Help

```python
import datacraft

# List all registered types:
datacraft.registered_types()
['calculate', 'char_class', 'cc-ascii', 'cc-lower', '...', 'uuid', 'values', 'replace', 'regex_replace']

# Print API usage for a specific type or types
print(datacraft.type_usage('char_class', 'replace', '...'))
# Example Output
"""
-------------------------------------
replace | API Example:

import datacraft

spec = {
 "field": {
   "type": "values",
   "data": ["foo", "bar", "baz"]
 },
 "replacement": {
   "type": "replace",
   "data": {"ba": "fi"},
   "ref": "field"
 }
}

print(*datacraft.entries(spec, 3), sep='\n')

{'field': 'foo', 'replacement': 'foo'}
{'field': 'bar', 'replacement': 'fir'}
{'field': 'baz', 'replacement': 'fiz'}
"""
```

For more detailed documentation please see: 
[datacraft.readthedocs.io](https://datacraft.readthedocs.io/en/latest/index.html)

