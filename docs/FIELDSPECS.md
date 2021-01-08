Field Spec Definitions
========================

# Overview
Each field that should be generated needs a specification that describes the way the values for it should be created. We
refer to this as a Field Spec.  The simplest type of Field Spec is a values spec.  The main format of a values spec is a
list of values to use.  These values are rotated through incrementally.  If the number of increments is larger than the
number of values in the list, the values start over from the beginning of the list. When combining values from two values
providers that are lists, they will be combined in incrementing order. i.e:

```json
{
  "combine": {"type": "combine", "refs":  ["ONE", "TWO"]},
  "refs": {
    "ONE":[ "A", "B", "C"],
    "TWO":[ 1, 2, 3]
  }
}
```

Will produce the values A1, B2, C3 continuously. 

```shell script
dist/datamaker -s ~/scratch/sample.json -i 7
A1
B2
C3
A1
B2
C3
A1
```
If an additional number is added to TWO, we now get 12 distinct values:

```json
{
  "combine": {"type": "combine", "refs":  ["ONE", "TWO"]},
  "refs": {
    "ONE":[ "A", "B", "C"],
    "TWO":[ 1, 2, 3, 4]
  }
}
```
```shell script
dist/datamaker -s ~/scratch/sample.json -i 12 | sort
A1
A2
A3
A4
B1
B2
B3
B4
C1
C2
C3
C4
```

## Field Spec Structure
There are two types of Field Specs, one is the full format that is valid for all types, and the other is the shorthand
for values types only.

### The full format.
The only required element is type. Each Type Handler requires different pieces of information. See the Field Type reference
below for details on each type.
```json
{ 
  "type": "<the type>",
  "config": {
    "key1": "value1",
    ...
    "keyN": "valueN"
  },
  "data": ["the data"],
  "ref": "REF_POINTER_IF_USED",
  "refs": [ "USES", "MORE", "THAN", "ONE"]
}
```

### Values Shorthand
The values type is very common and so has a shorthand notation.  Below is an example full Field Spec for some values types fields
and the same spec in shorthand notation.

```json
{
  "field1": { "type":  "vaules", "data":  [1, 2, 3, 4, 5]},
  "field2": { "type":  "values", "data":  {"A": 0.5, "B":  0.3, "C":  0.2}},
  "field3": { "type":  "values", "data":  "CONSTANT"}
}
```
```json
{
  "field1": [1, 2, 3, 4, 5],
  "field2": {"A": 0.5, "B":  0.3, "C":  0.2},
  "field3": "CONSTANT"
}
```

# Common Configurations
There are some configuration values that can be applied to all types.  These are listed below

| key   | effect |
|-------|--------|
|prefix | Prepends the value to all results |
|suffix | Appends the value to all results  |

Example:
```json
{ 
  "type": "values",
  "config": {
    "prefix": "Hello "
  },
  "data": ["world", "beautiful", "destiny"]
}
```

# Field Spec Types
These are the built in types

## Values
There are three types of values specs: Constants, List, and Weighted. Values specs have a shorthand notation where the
value of the data element replaces the full spec.  See examples below.

### Constant Values
A Constant Value is just a single value that is used in every iteration

```json
{ 
  "constant1": { "type": "values", "data":  42},
  "shorthand_constant": "This is simulated data and should not be used for nefarious purposes"
}
```

### List Values
List values are rotated through in order. If the number of iterations is larger than the size of the list, we start over
from the beginning of the list.

```json
{ 
  "list1": { "type": "values", "data":  ["200", "202", "303", "400", "404", "500"]},
  "shorthand_list": ["200", "202", "303", "400", "404", "500"]
}
```

### Weighted Values
Weighted values are generated according to their weights.

```json
{ 
  "weighted1": { 
    "type": "values", 
    "data":  {
      "200": 0.4, "202": 0.3, "303": 0.1,
      "400": 0.05, "403": 0.05, "404": 0.05, "500": 0.05
    }
  },
  "shorthand_weighted": {
      "200": 0.4, "202": 0.3, "303": 0.1,
      "400": 0.05, "403": 0.05, "404": 0.05, "500": 0.05
    }
}
```
The example above will generate 200 40% of the time and 400 and 403 5%. The higher the number of iterations the more likely
the values will match their specified weights.

## Combine
A combine Field Spec is used to concatenate or append two or more fields or reference to one another. 

The combine Field Spec structure is:
```json
{
  "<field name>": {
    "type": "combine",
    "fields": ["valid field name1", "valid field name2"],
    OR
    "refs": ["valid ref1", "valid ref2"],
    "config": { "join_with": "<optional string to use to join fields or refs, default is none"}
  }
}
```
Example below uses the first and last fields to create a full name field.
```json
{
  "full name": {
    "type": "combine",
    "fields": ["first", "last"],
    "config": { "join_with": " "}
  },
  "first": {
    "type": "values",
    "data": ["zebra", "hedgehog", "llama", "flamingo"]
  },
  "last": {
    "type": "values",
    "data": ["jones", "smith", "williams"]
  }
}
```

## Range
A range spec is used to generate a range of integers. The ranges are inclusive for start and end.

The weightedref Field Spec structure is:
```json
{
  "<field name>": {
    "type": "range",
    "data": [<start>, <end>, <step> (optional)]
  }
}
```
## Weighted Ref
A weighted ref spec is used to select the values from a set of refs in a weighted fashion. 

The weightedref Field Spec structure is:
```json
{
  "<field name>": {
    "type": "weightedref",
    "data": { "valid_ref_1": 0.N, "valid_ref_2": 0.N, ... }
  }
}
```
For example if we want to generate a set of HTTP response codes, but we want mostly success related codes we could use 
the follow spec.

```json
{
  "http_code": {
    "type": "weightedref",
    "data": {
        "GOOD_CODES": 0.7,
        "BAD_CODES": 0.3
    }
  },
  "refs": {
    "GOOD_CODES": { "200": 0.5, "202": 0.3, "203": 0.1, "300": 0.1},
    "BAD_CODES": { "400": 0.5, "403": 0.3, "404": 0.1, "500": 0.1}
  }
}
```

## Select List Subset
A select list subset spec is used to select multiple values from a list to use as the value for a field. 

The select_list_subset Field Spec structure is:
```json
{
  "<field name>": {
    "type": "select_list_subset",
    "config": {
      "mean": N,
      "stddev": N,
      "min": N,
      "max": N,
      "join_with": "<delimiter to join with>"
     },
    "data": ["data", "to", "select", "from"],
    OR
    "ref": "REF_WITH_DATA_AS_LIST"
  }
}
```

The join_with config option is used to specify how the selected values should be combined. The mean and stddev config 
options tell how many items should be chosen. For example a mean of 2 and stddev of 1, would mostly choose 2 items then
sometimes 1 or 3 or more. Set the stddev to 0 if only the exact number of items should be chosen (which is the default).
You can also set a min and max. Example:

```json
{
  "ingredients": {
    "type": "select_list_subset",
    "config": {
      "mean": 3,
      "stddev": 1,
      "min": 2,
      "max": 4,
      "join_with": ", "
    },
    "data": [ "onions", "mushrooms", "garlic", "bell peppers", "spinach", "potatoes", "carrots"]
  }
}
```
```shell script
dist/datamaker -s ~/scratch/ingredients.json -i 10
garlic, onions
garlic, spinach
bell peppers, spinach
mushrooms, bell peppers, carrots, potatoes
mushrooms, potatoes, bell peppers
potatoes, onions, garlic, bell peppers
potatoes, bell peppers, onions, garlic
spinach, bell peppers
spinach, onions, garlic
carrots, garlic, mushrooms, potatoes
```
