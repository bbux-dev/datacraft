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


def test_miss_match_logs_error(mocker):
    mocker.patch('yaml.load', return_value={'not': 'the same'})
    raw_spec = {"test": {"type": "values", "data": "for spec"}}
    # for test coverage
    datagen.spec_formatters.format_yaml(raw_spec)


def test_error_logged(mocker):
    mocker.patch('yaml.load', side_effect=Exception('uh oh'))
    raw_spec = {"test": {"type": "values", "data": "for spec"}}
    # for test coverage
    datagen.spec_formatters.format_yaml(raw_spec)


def test_other_format_hits():
    raw_spec = {
        "refs": {
            "ref_one": ["a", "b", "c"],
            "ref_two": ["d", "e", "f"]
        },
        "test": {"type": "combine", "refs": ["ref_one", "ref_two"], "not": "used"},
    }
    expected = """{
  "test": {
    "type": "combine",
    "refs": ["ref_one", "ref_two"],
    "not": "used"
  },
  "refs": {
    "ref_one": ["a", "b", "c"],
    "ref_two": ["d", "e", "f"]
  }
}"""
    formatted_spec = datagen.spec_formatters.format_json(raw_spec)
    assert formatted_spec == expected, f'Mismatch: \n{formatted_spec}\n{expected}'
