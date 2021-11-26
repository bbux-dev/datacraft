Built in Field Spec Type Schemas
================================


1. [Definitions](#definitions)
1. [calculate](#calculate)
1. [char_class](#char_class)
1. [combine-list](#combine-list)
1. [combine](#combine)
1. [config_ref](#config_ref)
1. [csv](#csv)
1. [Date types (data, date.iso, date.iso.us)](#date)
1. [geo.lat](#geo.lat)
1. [geo.long](#geo.long)
1. [geo.pair](#geo.pair)
1. [IP types (ip, ipv4)](#ip)
1. [Range types (range, rand_range)](#range)
1. [select_list_subset](#select_list_subset)
1. [unicode_range](#unicode_range)
1. [uuid](#uuid)
1. [values](#values)
1. [weighted_csv](#weighted_csv)


# <a name="definitions"></a>Definitions

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/definitions.json",
  "definitions": {
    "prefix": {
      "type": "string",
      "description": "Prefix string pre-pended to all values for field",
      "default": null,
      "examples": ["@", "www.", "<h1>", "#"]
    },
    "suffix": {
      "type": "string",
      "description": "Suffix string appended to all values for field",
      "default": null,
      "examples": [".com", "</h1>", "@"]
    },
    "quote": {
      "type": "string",
      "description": "String to surround all values for field with",
      "default": null,
      "examples": ["\"", "'", "||"]
    },
    "join_with": {
      "type": "string",
      "description": "String or character to join multiple values together with",
      "default": null,
      "examples": [",", "@", " OR ", " && "]
    },
    "affirmative_check": {
      "description": "Either true, false, 'on', 'off', 'yes', 'no', 'true', 'false', case insensitive",
      "oneOf": [
        {"type": "boolean"},
        {"type": "string", "pattern": "[t|T][r|R][u|U][e|E]|[f|F][a|A][l|L][s|S][e|E]|[y|Y][e|E][s|S]|[n|N][o|O]|[o|O][n|N]|[o|O][f|F][f|F]"}
      ]
    },
    "as_list": {
      "description": "If the values should be returned as a list. Either true, false, 'on', 'off', 'yes', 'no', 'true', 'false', case insensitive",
      "$ref": "#/definitions/affirmative_check"
    },
    "cast": {
      "type": "string",
      "description": "Type to cast values to for field",
      "examples": ["i", "int", "f", "float", "s", "str", "string", "h", "hex"],
      "enum": ["i", "int", "f", "float", "s", "str", "string", "h", "hex"]
    },
    "count": {
      "description": "Number of values to include, constant, list, or weighted values spec",
      "oneOf": [
        {"type": "integer"},
        {
          "type": "array",
          "minItems": 1,
          "uniqueItems": false,
          "items": {"type": "integer"}
        },
        {
          "type": "object",
          "minProperties": 1,
          "propertyNames": {
            "pattern": "[0-9]+"
          },
          "additionalProperties": {"type": "number"}
        }
      ]
    },
    "precision": {
      "type": "integer",
      "description": "How many digits after decimal point to include in values",
      "default": null,
      "examples": [0, 2, 7, 12],
      "minimum": 0
    },
    "bbox": {
      "type": "array",
      "description": "Bounding box for geo related points, describes lower left and upper right coordinates with longitude first",
      "default": null,
      "minItems": 4,
      "maxItems": 4,
      "items":[
        {"type": "number", "minimum": -180, "maximum": 180},
        {"type": "number", "minimum": -90, "maximum": 90},
        {"type": "number", "minimum": -180, "maximum": 180},
        {"type": "number", "minimum": -90, "maximum": 90}
      ]
    }
  }
}
```
</details>

# <a name="calculate"></a>calculate

Types covered by schema: `calculate`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/calculate.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {
      "type": "string",
      "pattern": "^calculate$"
    },
    "config": {
      "type": "object"
    },
    "refs": {
      "oneOf": [
        {
          "type": "object"
        },
        {
          "type": "array",
          "minItems": 1
        }
      ],
      "examples": [
        "{ \"ref_name\": \"alias\" }",
        "[ \"ref1\", \"ref2\" ]"
      ]
    },
    "fields": {
      "oneOf": [
        {
          "type": "object"
        },
        {
          "type": "array",
          "minItems": 1
        }
      ],
      "examples": [
        "{ \"field_name\": \"alias\" }",
        "[ \"field1\", \"field2\" ]"
      ]
    },
    "formula": {
      "type": "string",
      "examples": [
        "{{a}} * {{b}}",
        "{{a}} * 22.34",
        "({{a}} + {{b}} - {{c}}) * ({{d}}^^2)",
        "sqrt(exp({{ a }}))"
      ]
    }
  },
  "anyOf": [
    {
      "oneOf": [
        {"required": ["refs", "formula"]},
        {"required": ["fields", "formula"]}
      ]
    },
    {
      "oneOf": [
        {"required": ["refs", "fields", "formula"]}
      ]
    }
  ]

}
```
</details>

# <a name="char_class"></a>char_class

Types covered by schema: `char_class`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/char_class.schema.json",
  "type": "object",
  "required": ["type", "data"],
  "properties": {
    "type": {"type": "string", "pattern": "^char_class$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "min": {
          "type": "integer",
          "description": "minimum number of characters in string",
          "default": null,
          "examples": [1, 7, 2255],
          "minimum": 1
        },
        "max": {
          "type": "integer",
          "description": "maximum number of characters in string",
          "default": null,
          "examples": [1, 7, 2255],
          "minimum": 1
        },
        "mean": {
          "type": "number",
          "description": "mean number of characters in string",
          "default": null,
          "examples": [3, 5, 7.5]
        },
        "stddev": {
          "type": "number",
          "description": "standard deviation from mean for number of characters in string",
          "default": null,
          "examples": [0.5, 3, 7]
        }
      },
      "not": {
        "description": "count should not be present if min max or mean are present",
        "anyOf": [
          {"required": ["count", "min"]},
          {"required": ["count", "max"]},
          {"required": ["count", "mean"]}
        ]
      }
    },
    "data": {
      "oneOf": [
        {
          "description": "arbitrary user defined characters or one of predefined character classes: ascii, lower, upper, digits, letters, word, printable, visible, punctuation, special, hex, hex-lower, hex-upper",
          "type": "string"
        },
        {
          "description": "array of one or more of the above",
          "type": "array",
          "minItems": 1,
          "items": {"type": "string"}
        }
      ]
    }
  }
}
```
</details>

# <a name="combine-list"></a>combine-list

Types covered by schema: `combine-list`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/combine.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^combine-list$"},
    "config": {
      "type": "object",
      "properties": {
        "join_with": {"$ref": "#/definitions/join_with"},
        "as_list": {"$ref": "#/definitions/as_list"}
      }
    },
    "refs": {
      "type": "array",
      "uniqueItems": false,
      "items": {
        "type": "array",
        "minItems": 2,
        "items": {
          "type": "string"
        }
      }
    },
    "fields": {
      "type": "array",
      "uniqueItems": true,
      "items": {
        "type": "array",
        "minItems": 2,
        "items": {
          "type": "string"
        }
      }
    }
  },
  "oneOf": [
    {"required": ["refs"]},
    {"required": ["fields"]}
  ]
}
```
</details>

# <a name="combine"></a>combine

Types covered by schema: `combine`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/combine.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^combine$"},
    "config": {
      "type": "object",
      "properties": {
        "join_with": {"$ref": "#/definitions/join_with"},
        "as_list": {"$ref": "#/definitions/as_list"}
      }
    },
    "refs": {
      "type": "array",
      "minItems": 2,
      "uniqueItems": true,
      "items": {
        "type": "string"
      }
    },
    "fields": {
      "type": "array",
      "minItems": 2,
      "uniqueItems": true,
      "items": {
        "type": "string"
      }
    }
  },
  "oneOf": [
    {"required": ["refs"]},
    {"required": ["fields"]}
  ]
}
```
</details>

# <a name="config_ref"></a>config_ref

Types covered by schema: `config_ref`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/config_ref.schema.json",
  "type": "object",
  "description": "Type used to store configurations that are used across multiple fields",
  "required": ["type", "config"],
  "properties": {
    "type": {
      "type": "string",
      "pattern": "^config_ref$"
    },
    "config": {
      "type": "object"
    }
  }
}
```
</details>

# <a name="csv"></a>csv

Types covered by schema: `csv`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/csv.schema.json",
  "type": "object",
  "required": ["type", "config"],
  "properties": {
    "type": {  "type": "string", "pattern": "^csv$"},
    "config": {
      "type": "object",
      "anyOf": [
        {"required": ["datafile"]},
        {"required": ["config_ref", "column"]}
      ],
      "properties": {
        "datafile": {
          "type": "string",
          "description": "Name of file in data directory that contains the data for this field",
          "examples": [
            "example.csv",
            "subdir/example2.csv"
          ]
        },
        "config_ref": {
          "type": "string",
          "description": "Name of config_ref to use to populate config for this field",
          "examples": ["tabs_config", "common_csv_config"]
        },
        "headers": {
          "description": "If the csv file has headers",
          "default": false,
          "$ref": "#/definitions/affirmative_check"
        },
        "column": {
          "type": ["number", "string"],
          "description": "1 based column number or field name if headers are present",
          "default": 1,
          "minimum": 1,
          "examples": [
            1,
            "col_2",
            "name"
          ]
        },
        "delimiter": {
          "type": "string",
          "description": "how values are separated in the csv file, default is comma",
          "default": ",",
          "examples": [
            ",", "\t", ";", " "
          ]
        },
        "quotechar": {
          "type": "string",
          "description": "how values are quoted, default is double quote",
          "default": "\"",
          "examples": [
            ",", "\t", ";", " "
          ]
        },
        "sample": {
          "description": "If the values for the field should be selected at random from the values in the column, default is false",
          "default": false,
          "$ref": "#/definitions/affirmative_check"
        },
        "count": {
          "$ref": "#/definitions/count",
          "description": "Number of values in column to use for field",
          "default": 1
        },
        "join_with": {"$ref": "#/definitions/join_with"},
        "as_list": {"$ref": "#/definitions/as_list"}
      }
    }
  }
}
```
</details>

# <a name="date"></a>Date types (data, date.iso, date.iso.us)

Types covered by schema: `date, date.iso, date.iso.us`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/date.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^date(\\.iso|\\.iso\\.us)?$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "format": {
          "description": "Valid datetime format string",
          "default": "%d-%m-%Y",
          "examples": [
            "%Y%m%d",
            "%m/%d/%Y",
            "%H:%M:%S"
          ],
          "type": "string"
        },
        "duration_days": {
          "description": "The number of days from the start date to create date strings for",
          "default": 30,
          "examples": [
            1, 30, 90, 9999
          ],
          "oneOf": [
            {
              "type": "number",
              "minimum": 0
            },
            {
              "type": "string",
              "pattern": "[1-9][0-9]*"
            }
          ]
        },
        "start": {
          "type": "string",
          "default": null,
          "description": "date string matching format or default format to use for start date",
          "examples": [
            "22-02-2022", "02/22/1972", "2009-09-01T08:08.000Z"
          ]
        },
        "end": {
          "type": "string",
          "default": null,
          "description": "date string matching format or default format to use for end date",
          "examples": [
            "22-02-2022", "02/22/1972", "2009-09-01T08:08.000Z"
          ]
        },
        "offset": {
          "type": "integer",
          "description": "number of days to shift base date by, positive means shift backwards, negative means forward",
          "default": 0,
          "examples": [
            30, -30, 365, 730
          ]
        },
        "center_date": {
          "type": "string",
          "default": null,
          "description": "date string matching format or default format to use for center date",
          "examples": [
            "22-02-2022", "02/22/1972", "2009-09-01T08:08.000Z"
          ]
        },
        "stddev_days": {
          "description": "The standard deviation in days from the center date that dates should be distributed",
          "default": 15,
          "examples": [
            1, 12, 720
          ],
          "oneOf": [
            {
              "type": "number",
              "minimum": 0
            },
            {
              "type": "string",
              "pattern": "[1-9][0-9]*"
            }
          ]
        }
      },
      "not": {
        "description": "center_date and stddev_days should not appear with start, end, or duration_days",
        "anyOf": [
          {"required": ["center_date", "start"]},
          {"required": ["center_date", "end"]},
          {"required": ["center_date", "duration_days"]},
          {"required": ["stddev_days", "start"]},
          {"required": ["stddev_days", "end"]},
          {"required": ["stddev_days", "duration_days"]}
        ]
      }
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="geo.lat"></a>geo.lat

Types covered by schema: `geo.lat`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/geo.lat.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {"type": "string", "pattern": "^geo\\.lat$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "precision": {"$ref": "#/definitions/precision"},
        "bbox": {"$ref": "#/definitions/bbox"},
        "start_lat": {"type": "number", "minimum": -90, "maximum": 90},
        "end_lat": {"type": "number", "minimum": -90, "maximum": 90}
      },
      "additionalProperties": false
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="geo.long"></a>geo.long

Types covered by schema: `geo.long`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/geo.lat.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^geo\\.long$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "precision": {"$ref": "#/definitions/precision"},
        "bbox": {"$ref": "#/definitions/bbox"},
        "start_long": {"type": "number", "minimum": -180, "maximum": 180},
        "end_long": {"type": "number", "minimum": -180, "maximum": 180}
      },
      "additionalProperties": false
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="geo.pair"></a>geo.pair

Types covered by schema: `geo.pair`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/geo.lat.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^geo\\.pair$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "precision": {"$ref": "#/definitions/precision"},
        "bbox": {"$ref": "#/definitions/bbox"},
        "start_lat": {"type": "number", "minimum": -90, "maximum": 90},
        "end_lat": {"type": "number", "minimum": -90, "maximum": 90},
        "start_long": {"type": "number", "minimum": -180, "maximum": 180},
        "end_long": {"type": "number", "minimum": -180, "maximum": 180},
        "join_with": {"$ref": "#/definitions/join_with"},
        "as_list": {"$ref": "#/definitions/as_list"},
        "lat_first": {"$ref": "#/definitions/affirmative_check"}
      },
      "additionalProperties": false
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="ip"></a>IP types (ip, ipv4)

Types covered by schema: `ip, ipv4`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/date.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^ip(v4)?$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "base": {
          "description": "base of ip address",
          "examples": ["192", "10.", "100.100", "192.168.", "10.10.10"],
          "type": "string",
          "pattern": "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.?){1,4}$"
        },
        "cidr": {
          "description": "cidr notation i.e. 192.168.0.0/16, only /8 /16 /24 supported",
          "examples": ["192.168.0.0/24", "10.0.0.0/16", "100.0.0.0/8"],
          "type": "string",
          "pattern": "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])/(8|16|24)$"
        }
      },
      "not": {
        "description": "cidr and base should not both be specified",
        "anyOf": [
          {"required": ["cidr", "base"]}
        ]
      }
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="range"></a>Range types (range, rand_range)

Types covered by schema: `range, rand_range`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/range.schema.json",
  "type": "object",
  "required": ["type", "data"],
  "properties": {
    "type": {  "type": "string", "pattern": "^(rand_)?range$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "cast": {"$ref": "#/definitions/cast"},
        "precision": {"$ref": "#/definitions/precision"}
      }
    },
    "data": {
      "oneOf": [
        {
          "type": "array",
          "minItems": 1,
          "maxItems": 3,
          "uniqueItems": false,
          "items": { "type": "number" }
        },
        {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "uniqueItems": false,
            "items": { "type": "number" }
          }
        }
      ]
    }
  }
}
```
</details>

# <a name="select_list_subset"></a>select_list_subset

Types covered by schema: `select_list_subset`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/select_list_subset.schema.json",
  "type": "object",
  "required": ["type"],
  "oneOf": [
    {"required": ["ref"]},
    {"required": ["data"]}
  ],
  "properties": {
    "type": {"type": "string", "pattern": "^select_list_subset$"},
    "config": {
      "type": "object",
      "oneOf": [
        {"required": ["count"]},
        {"required": ["mean"]}
      ],
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "min": {
          "type": "integer",
          "description": "minimum number of items to select from list",
          "default": null,
          "examples": [1, 7, 2255],
          "minimum": 1
        },
        "max": {
          "type": "integer",
          "description": "maximum number of items to select from list",
          "default": null,
          "examples": [1, 7, 2255],
          "minimum": 1
        },
        "mean": {
          "type": "number",
          "description": "mean number of items to select from list",
          "default": null,
          "examples": [3, 5, 7.5]
        },
        "stddev": {
          "type": "number",
          "description": "standard deviation from mean for number of items to select from list",
          "default": null,
          "examples": [0.5, 3, 7]
        },
        "count": {
          "type": "number",
          "description": "exact number of items to select from list",
          "default": null,
          "minimum": 1,
          "examples": [3, 5, 7]
        }
      },
      "not": {
        "description": "count should not be present if min max or mean are present",
        "anyOf": [
          {"required": ["count", "min"]},
          {"required": ["count", "max"]},
          {"required": ["count", "mean"]}
        ]
      }
    },
    "ref": {
      "type": "string",
      "description": "The valid name of a spec from the ref section the contains a list as the data element"
    },
    "data": {
      "type": "array",
      "description": "The data to select from",
      "minItems": 1
    }
  }
}
```
</details>

# <a name="unicode_range"></a>unicode_range

Types covered by schema: `unicode_range`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/char_class.schema.json",
  "type": "object",
  "required": ["type", "data"],
  "properties": {
    "type": {"type": "string", "pattern": "^unicode_range$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"},
        "min": {
          "type": "integer",
          "description": "minimum number of characters in string",
          "default": null,
          "examples": [1, 7, 2255],
          "minimum": 1
        },
        "max": {
          "type": "integer",
          "description": "maximum number of characters in string",
          "default": null,
          "examples": [1, 7, 2255],
          "minimum": 1
        },
        "mean": {
          "type": "number",
          "description": "mean number of characters in string",
          "default": null,
          "examples": [3, 5, 7.5]
        },
        "stddev": {
          "type": "number",
          "description": "standard deviation from mean for number of characters in string",
          "default": null,
          "examples": [0.5, 3, 7]
        }
      },
      "not": {
        "description": "count should not be present if min max or mean are present",
        "anyOf": [
          {"required": ["count", "min"]},
          {"required": ["count", "max"]},
          {"required": ["count", "mean"]}
        ]
      }
    },
    "data": {
      "oneOf": [
        {
          "type": "array",
          "minItems": 2,
          "maxItems": 2,
          "uniqueItems": false,
          "items": {
            "oneOf": [
              {"type": "string", "pattern": "(0x)?[0-9a-fA-F]{4}"},
              {"type": "integer"}
            ]
          }
        },
        {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "uniqueItems": false,
            "items": {
              "oneOf": [
                {"type": "string", "pattern": "(0x)?[0-9a-fA-F]{4}"},
                {"type": "integer"}
              ]
            }
          }
        }
      ]
    }
  }
}
```
</details>

# <a name="uuid"></a>uuid

Types covered by schema: `uuid`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/uuid.schema.json",
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": {  "type": "string", "pattern": "^uuid$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"}
      }
    },
    "additionalProperties": false
  }
}
```
</details>

# <a name="values"></a>values

Types covered by schema: `values`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/values.schema.json",
  "type": "object",
  "required": ["data"],
  "properties": {
    "type": {  "type": "string", "pattern": "^values$"},
    "config": {
      "type": "object",
      "properties": {
        "prefix": {"$ref": "#/definitions/prefix"},
        "suffix": {"$ref": "#/definitions/suffix"},
        "quote": {"$ref": "#/definitions/quote"},
        "count": {"$ref": "#/definitions/count"}
      }
    },
    "data": {
      "oneOf": [
        { "type":  "string"},
        { "type":  "number"},
        { "type":  "boolean"},
        {
          "type": "array",
          "minItems": 1,
          "uniqueItems": false
        },
        {
          "type": "object",
          "minProperties": 1,
          "additionalProperties": { "type": "number" }
        }
      ]
    }
  }
}
```
</details>

# <a name="weighted_csv"></a>weighted_csv

Types covered by schema: `weighted_csv`

<details>
  <summary>JSON Schema</summary>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/bbux-dev/datagen/schemas/weighted_csv.schema.json",
  "type": "object",
  "required": ["type", "config"],
  "properties": {
    "type": {  "type": "string", "pattern": "^weighted_csv$"},
    "config": {
      "type": "object",
      "anyOf": [
        {"required": ["datafile"]},
        {"required": ["config_ref", "column"]}
      ],
      "properties": {
        "datafile": {
          "type": "string",
          "description": "Name of file in data directory that contains the data for this field",
          "examples": [
            "example.csv",
            "subdir/example2.csv"
          ]
        },
        "config_ref": {
          "type": "string",
          "description": "Name of config_ref to use to populate config for this field",
          "examples": ["tabs_config", "common_csv_config"]
        },
        "headers": {
          "description": "If the csv file has headers",
          "default": false,
          "$ref": "#/definitions/affirmative_check"
        },
        "column": {
          "type": ["number", "string"],
          "description": "1 based column number or field name if headers are present",
          "default": 1,
          "minimum": 1,
          "examples": [
            1,
            "col_2",
            "name"
          ]
        },
        "weight_column": {
          "type": ["number", "string"],
          "description": "1 based column number or field name if headers are present where weights are defined",
          "default": 2,
          "minimum": 1,
          "examples": [
            1,
            "col_2",
            "name"
          ]
        },
        "delimiter": {
          "type": "string",
          "description": "how values are separated in the csv file, default is comma",
          "default": ",",
          "examples": [
            ",", "\t", ";", " "
          ]
        },
        "quotechar": {
          "type": "string",
          "description": "how values are quoted, default is double quote",
          "default": "\"",
          "examples": [
            ",", "\t", ";", " "
          ]
        },
        "count": {
          "$ref": "#/definitions/count",
          "description": "Number of values in column to use for field",
          "default": 1
        },
        "join_with": {"$ref": "#/definitions/join_with"},
        "as_list": {"$ref": "#/definitions/as_list"}
      }
    }
  }
}
```
</details>

