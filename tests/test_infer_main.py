import argparse
import os
import pytest
from datacraft._infer import __main__ as entrypoint

test_dir = f'{os.path.dirname(os.path.realpath(__file__))}/data'


# Test with no arguments
def test_no_args():
    with pytest.raises(SystemExit):  # Assuming the program exits with no args
        entrypoint.main([])


# Test CSV input
def test_csv_input():
    csv_file = os.path.join(test_dir, 'test.csv')
    entrypoint.main(['--csv', csv_file])


# Test JSON input
def test_json_input():
    json_file = os.path.join(test_dir, 'to_infer_from.json')
    entrypoint.main(['--json', json_file])


# Test CSV directory input
def test_csv_dir_input():
    csv_dir = os.path.join(test_dir, 'csvs')
    entrypoint.main(['--csv-dir', csv_dir])


# Test JSON directory input
def test_json_dir_input():
    json_dir = os.path.join(test_dir, 'jsons')
    entrypoint.main(['--json-dir', json_dir])


# Test output file
def test_output_file(tmpdir):
    output_file = os.path.join(tmpdir, 'output.txt')
    csv_file = os.path.join(test_dir, 'test.csv')
    entrypoint.main(['--csv', csv_file, '--output', output_file])

    assert os.path.exists(output_file)


# Test limit option
def test_limit_option():
    csv_file = os.path.join(test_dir, 'test.csv')
    entrypoint.main(['--csv', csv_file, '--limit', '10'])


# Test duplication threshold
def test_duplication_threshold():
    csv_file = os.path.join(test_dir, 'test.csv')
    entrypoint.main(['--csv', csv_file, '-dt', '0.5'])


@pytest.mark.parametrize('threshold', [1.5, "foo"])
def test_invalid_duplication_thresholds(threshold):
    with pytest.raises(argparse.ArgumentTypeError):
        entrypoint.valid_range(threshold)


# Test log level
def test_log_level():
    csv_file = os.path.join(test_dir, 'test.csv')
    entrypoint.main(['--csv', csv_file, '-l', 'debug'])
