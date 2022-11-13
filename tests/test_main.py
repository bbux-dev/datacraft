import os

import catalogue
import pytest

import datacraft
from datacraft import __main__ as entrypoint

test_dir = f'{os.path.dirname(os.path.realpath(__file__))}/data'


def test_parse_empty_args():
    with pytest.raises(datacraft.SpecException):
        entrypoint.main([])


def test_parse_custom_code():
    entrypoint.main(['-c', os.path.join(test_dir, 'custom.py'), '--inline', '{}'])

    # verify string_reverser is now in registry
    handler = datacraft.registries.lookup_type('string_reverser')
    assert handler is not None


def test_parse_defaults_file():
    args = ['--defaults', os.path.join(test_dir, 'new_defaults.json'), '--inline', '{}']
    _test_default_is_changed('date_format', args, "%Y-%m-%d")


def test_parse_set_defaults():
    args = ['--set-defaults', 'date_format=%Y-%m-%d', '--inline', '{}']
    _test_default_is_changed('date_format', args, "%Y-%m-%d")


def test_parse_set_default_invalid_ignored():
    args = ['--set-defaults', 'incorrect_format', 'is_valid=should_exist', '--inline', '{}']
    entrypoint.main(args)
    with pytest.raises(catalogue.RegistryError):
        datacraft.registries.get_default('incorrect_format')


def test_parse_sample_mode():
    args = ['--sample-lists', '--inline', '{}']
    _test_default_is_changed('sample_mode', args, True)


def _test_default_is_changed(key, args, expected):
    orig_value = datacraft.registries.get_default(key)
    entrypoint.main(args)
    new_value = datacraft.registries.get_default(key)
    # reset default in registry
    datacraft.registries.set_default(key, orig_value)
    assert orig_value != new_value
    assert new_value == expected, f'{key} changed with args {args}, expected {expected}, but got {new_value}'


def test_parse_debug_spec(tmpdir):
    args = ['--debug-spec', '-o', str(tmpdir), '--inline', '{foo: [1,2,3]}']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_debug_spec_yaml(tmpdir):
    args = ['--debug-spec-yaml', '-o', str(tmpdir), '--inline', '{foo: [1,2,3]}']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_debug_defaults(tmpdir):
    args = ['--debug-defaults', '-o', str(tmpdir)]
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'dataspec_defaults.json'))


def test_parse_debug_defaults(tmpdir):
    args = ['--debug-defaults', '-o', str(tmpdir)]
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'dataspec_defaults.json'))


def test_parse_apply_raw(tmpdir):
    args = ['-o', str(tmpdir),
            '--apply-raw',
            '-t', os.path.join(test_dir, 'template.jinja'),
            '--inline', '{"A": 1, "B":2, "C": 3}']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_template_output(tmpdir):
    args = ['-o', str(tmpdir),
            '-t', os.path.join(test_dir, 'template.jinja'),
            '--inline', '{"A": 1, "B":2, "C": 3}']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_template_output_inline(tmpdir):
    args = ['-o', str(tmpdir),
            '-t', 'A:{{ A }}, B:{{ B }}, C:{{ C }}',
            '--inline', '{"A": 1, "B":2, "C": 3}']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_format_output(tmpdir):
    args = ['-o', str(tmpdir),
            '--format', 'json',
            '--inline', '{"A": 1, "B":2, "C": 3}']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_spec_and_inline_invalid():
    args = ['--spec', os.path.join(test_dir, 'spec.json'),
            '--inline', '{"A": 1, "B":2, "C": 3}']
    with pytest.raises(datacraft.SpecException):
        entrypoint.main(args)


def test_parse_spec_invalid_path():
    args = ['--spec', os.path.join(test_dir, 'spec_not_there.json')]
    # just for test coverage
    entrypoint.main(args)


def test_parse_spec_not_json_or_yaml():
    args = ['--spec', os.path.join(test_dir, 'blank_file')]
    with pytest.raises(datacraft.SpecException):
        entrypoint.main(args)


def test_parse_spec_yaml_format(tmpdir):
    args = ['--spec', os.path.join(test_dir, 'spec.yaml'),
            '-o', str(tmpdir),
            '-i', '5']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_inline_yaml(tmpdir):
    args = ['-o', str(tmpdir),
            '--format', 'json',
            '--inline', '{A: 1, B: [2, 4, 6], C: 3}',
            '-i', '5']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_inline_yaml_blank_string():
    args = ['--format', 'json',
            '--inline', ' ']
    with pytest.raises(datacraft.SpecException):
        entrypoint.main(args)


def test_wrap_main(tmpdir):
    args = ['test_main.py',
            '-o', str(tmpdir),
            '--format', 'json',
            '--inline', ' ']
    import sys
    sys.argv = args
    # for coverage
    entrypoint.wrap_main()


def test_server(tmpdir, mocker):
    mocker.patch('datacraft.server.run', side_effect=ModuleNotFoundError())
    args = ['--format', 'json',
            '--inline', '{A: 1, B: [2, 4, 6], C: 3}',
            '-i', '5', '--server']
    entrypoint.main(args)


def test_var_file_not_there(tmpdir):
    args = ['--format', 'json',
            '--inline', '{ {{ first }}: 1, {{ second }}: [2, 4, 6], {{ third }}: 3}',
            '-i', '5',
            '-o', str(tmpdir),
            '--var-file', '/cant/find/vars.json']
    entrypoint.main(args)
    assert not os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_var_file(tmpdir):
    args = ['--format', 'json',
            '--inline', '{ {{ first }}: 1, {{ second }}: [2, 4, 6], {{ third }}: 3}',
            '-i', '5',
            '-o', str(tmpdir),
            '--var-file', os.path.join(test_dir, 'vars.json')]
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_var_args(tmpdir):
    args = ['--format', 'json',
            '--inline', '{ {{ first }}: 1, {{ second }}: [2, 4, 6], {{ third }}: 3}',
            '-i', '5',
            '-o', str(tmpdir),
            '--vars', 'first=a', 'second=b', 'third=c']
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_template_spec_with_vars(tmpdir):
    args = ['--spec', os.path.join(test_dir, 'templated_spec.json'),
            '--vars', 'pet_count=2',
            '-i', '5',
            '-o', str(tmpdir)]
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'generated-0'))


def test_parse_not_json_or_yaml(tmpdir):
    args = ['--spec', os.path.join(test_dir, 'not_json_or_yaml.blah'),
            '-i', '5',
            '-o', str(tmpdir)]
    with pytest.raises(datacraft.SpecException):
        entrypoint.main(args)


def test_var_args_not_all_defined(tmpdir):
    args = ['--format', 'json',
            '--inline', '{ {{ first }}: 1, {{ second }}: [2, 4, 6], {{ third }}: 3}',
            '-i', '5',
            '-o', str(tmpdir),
            '--vars', 'first=a', 'third=c']  # missing second
    with pytest.raises(datacraft.SpecException):
        entrypoint.main(args)


def test_var_args_not_all_defined_no_assignment(tmpdir):
    args = ['--format', 'json',
            '--inline', '{ {{ first }}: 1, {{ second }}: [2, 4, 6], {{ third }}: 3}',
            '-i', '5',
            '-o', str(tmpdir),
            '--vars', 'first=a', 'second', 'third=c']  # missing second
    with pytest.raises(datacraft.SpecException):
        entrypoint.main(args)


format_key_tests = [
    ('--type-list', 'type_list.txt'),
    ('--type-help', 'type_help.txt'),
    ('--cast-list', 'cast_list.txt'),
    ('--format-list', 'format_list.txt'),
]


@pytest.mark.parametrize("info_flag,filename", format_key_tests)
def test_write_info_file_created(info_flag, filename, tmpdir):
    args = [info_flag, '-o', str(tmpdir)]
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, filename))


def test_type_help_with_filter(tmpdir):
    args = ['--type-help', 'calculate', 'sample', '-o', str(tmpdir)]
    entrypoint.main(args)
    assert os.path.exists(os.path.join(tmpdir, 'type_help.txt'))
