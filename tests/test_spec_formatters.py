import pytest

import datagen


def test_format_json():
    raw_spec = {
        "dates": {
            "config": {
                "format": "%Y%m%d %H:%M",
                "center_date": "20500601 12:00",
                "stddev_days": "2"
            },
            "type": "date",
        }
    }
    expected = """{
  "dates": {
    "type": "date",
    "config": {
      "format": "%Y%m%d %H:%M",
      "center_date": "20500601 12:00",
      "stddev_days": "2"
    }
  }
}"""
    formatted_spec = datagen.spec_formatters.format_json(raw_spec)
    assert formatted_spec == expected, f'Mismatch: \n{formatted_spec}\n{expected}'


def test_format_yaml():
    raw_spec = {
        "dates": {
            "config": {
                "format": "%Y%m%d %H:%M",
                "center_date": "20500601 12:00",
                "stddev_days": "2"
            },
            "type": "date",
        }
    }
    expected = """dates:
  type: date
  config:
    format: '%Y%m%d %H:%M'
    center_date: 20500601 12:00
    stddev_days: '2'"""
    formatted_spec = datagen.spec_formatters.format_yaml(raw_spec)
    assert formatted_spec == expected, f'Mismatch: \n{formatted_spec}\n{expected}'


def test_format_json_refs():
    raw_spec = {
        "refs": {
            "ref_one": ["a", "b", "c"],
            "ref_two": ["d", "e", "f"]
        },
        "test": {"type": "ref", "data": "ref_one"},
    }
    expected = """{
  "test": {
    "type": "ref",
    "data": "ref_one"
  },
  "refs": {
    "ref_one": ["a", "b", "c"],
    "ref_two": ["d", "e", "f"]
  }
}"""
    formatted_spec = datagen.spec_formatters.format_json(raw_spec)
    assert formatted_spec == expected, f'Mismatch: \n{formatted_spec}\n{expected}'
