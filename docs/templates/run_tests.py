import re
import json
import subprocess


def single_command(name, info):
    cmd = info['command']
    out = subprocess.check_output(cmd, shell=True).decode("utf-8")
    match = info['match']
    if match and 'lines' in match:
        _verify_lines(match, out)
    if match and 'exact' in match:
        clean = out.strip().replace('\r\n', '\n')
        assert clean == match['exact'].strip(), f"Output differs from expected, actual: {out.strip()}"


def _verify_lines(match, out):
    expected_lines = match['lines']
    pattern = re.compile(match['pattern'])
    # non blank parts
    out_parts = [p for p in out.split('\n') if p.strip() != '']
    # verify non blank lines is expected number
    assert len(out_parts) == expected_lines
    # verify pattern of output matches expected
    non_matches = [line for line in out_parts if pattern.match(line) is None]
    assert len(non_matches) == 0, f"Not all lines match pattern: {match['pattern']}"


def multi_command(name, info):
    for _, details in info.items():
        single_command(name, details)


def test_commands():
    with open('tests.json') as f:
        data = json.load(f)
    for name, info in data.items():
        if 'command' in info:
            single_command(name, info)
        elif 'commands' in info:
            multi_command(name, info['commands'])
