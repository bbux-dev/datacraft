DATA = {
  "types": [
    {
      "name": "values ",
      "short": "constant, list, or weighted dictionary",
      "prototype": """
{
    "field_name": {
        "type": "range",
        "data": Union[str, bool, int, float, list, dict],
        "config": {
            "key": Any
        }
    }
}""",
      "examples": [
        {"field_constant": {"type": "values", "data": 42}},
        {"field_list": {"type": "values", "data": [1, 2, 3, 5, 8, 13]}},
        {"field_weighted": {"type": "values", "data": {"200": 0.6, "404": 0.1, "303": 0.3}}},
        {"field_constant": 42},
        {"field_list": [1, 2, 3, 5, 8, 13]},
        {"field_weighted": {"200": 0.6, "404": 0.1, "303": 0.3}}
      ]
    },
    {
      "name": "range ",
      "short": "range of values",
      "prototype": """
{
  "<field name>": {
    "type": "range",
    "data": [<start>, <end>, <step> (optional)],
    or
    "data": [
      [<start>, <end>, <step> (optional)],
      [<start>, <end>, <step> (optional)],
      ...
      [<start>, <end>, <step> (optional)],
    ],
    "config": {
      "key": Any
    }
  }
}

start: (Union[int, float]) - start of range
end: (Union[int, float]) - end of range
step: (Union[int, float]) - step for range, default is 1
      """,
      "examples": [
        "{\n  \"zero_to_ten_step_half\": {\n    \"type\": \"range\",\n    \"data\": [0, 10, 0.5]\n  }\n}",
        "{\n  \"range_shorthand1:range\": {\n    \"data\": [0, 10, 0.5]\n  }\n}",
        "{\"range_shorthand2:range\": [0, 10, 0.5]}"
      ]
    },
    {
      "name": "rand_range ",
      "short": "random value in a range",
      "prototype": """
{
  "<field name>": {
    "type": "rand_range",
    "data": [<upper>],
    or
    "data": [<lower>, <upper>],
    or
    "data": [<lower>, <upper>, <precision> (optional)]
  }
}

upper: (Union[int, float]) - upper limit of random range
lower: (Union[int, float]) - lower limit of random range
precision: (int) - Number of digits after decimal point      
      """
    },
    {
      "name": "combine ",
      "short": "refs or fields"
    },
    {
      "name": "combine-list ",
      "short": "list of lists of refs to combine"
    },
    {
      "name": "date ",
      "short": "date strings"
    },
    {
      "name": "date.iso ",
      "short": "date strings in ISO8601 format no microseconds"
    },
    {
      "name": "date.iso.us ",
      "short": "date strings in ISO8601 format w/ microseconds"
    },
    {
      "name": "uuid ",
      "short": "generates valid uuid"
    },
    {
      "name": "char_class ",
      "short": "generates strings from character classes"
    },
    {
      "name": "unicode_range ",
      "short": "generates strings from unicode ranges"
    },
    {
      "name": "geo.lat ",
      "short": "generates decimal latitude"
    },
    {
      "name": "geo.long ",
      "short": "generates decimal longitude"
    },
    {
      "name": "geo.pair ",
      "short": "generates long,lat pair"
    },
    {
      "name": "ip/ipv4 ",
      "short": "generates ip v4 addresses"
    },
    {
      "name": "ip.precise ",
      "short": "generates ip v4 addresses"
    },
    {
      "name": "weightedref ",
      "short": "produces values from refs in weighted fashion"
    },
    {
      "name": "select_list_subset ",
      "short": "selects subset of fields that are combined to create the value for the field"
    },
    {
      "name": "csv ",
      "short": "Uses external csv file to supply data"
    },
    {
      "name": "csv_select ",
      "short": "Efficient way to select multiple csv columns"
    },
    {
      "name": "nested ",
      "short": "For nested fields"
    },
    {
      "name": "calculate ",
      "short": "Calculate values from output of other fields or refs"
    }
  ]
}