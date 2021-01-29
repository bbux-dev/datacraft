import os
from dataspec import outputs
from dataspec import template_engines as engines

test_dir = f'{os.path.dirname(os.path.realpath(__file__))}'
outdir = f'{test_dir}/../build'


def test_outputs_single_field():
    # for coverage
    writer = outputs.FileWriter(
        outdir=outdir,
        outname='test_single',
        extension='txt',
        records_per_file=1
    )
    output = outputs.SingleFieldOutput(writer, True)
    output.handle('key', 'value')
    output.finished_record()

    _verify_ouput('test_single-0.txt', 'key -> value\n')


def test_outputs_record_level():
    # for coverage
    writer = outputs.FileWriter(
        outdir=outdir,
        outname='test_record',
        extension='txt',
        records_per_file=1
    )

    engine = engines.load(f'{test_dir}/data/template.jinja')
    output = outputs.RecordLevelOutput(engine, writer)

    # template looks like: A:{{ A }}, B:{{ B }}, C:{{ C }}
    output.handle('A', '1')
    output.handle('B', '2')
    output.handle('C', '3')
    output.handle('D', '4')
    output.finished_record()

    _verify_ouput('test_record-0.txt', 'A:1, B:2, C:3\n')


def _verify_ouput(fild_name, expected_content):
    with open(f'{outdir}/{fild_name}') as handle:
        content = handle.read()

    assert expected_content == content
