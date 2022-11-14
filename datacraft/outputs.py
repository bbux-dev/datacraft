"""
Module holds output related classes and functions
"""
from typing import Union
from abc import ABC, abstractmethod
import os
import json
import logging
from pathlib import Path
import catalogue  # type: ignore
import yaml
from . import template_engines, registries, utils
from .supplier.model import RecordProcessor, OutputHandlerInterface
from .exceptions import SpecException

_log = logging.getLogger(__name__)


@registries.Registry.formats('json')
def _format_json(record: Union[list, dict]) -> str:
    """formats the record as compressed json  """
    return json.dumps(record, ensure_ascii=registries.get_default('format_json_ascii'))


@registries.Registry.formats('json-pretty')
def _format_json_pretty(record: Union[list, dict]) -> str:
    """pretty prints the record as json  """
    format_json_ascii = utils.is_affirmative('', {}, registries.get_default('format_json_ascii'))
    return json.dumps(record, indent=int(registries.get_default('json_indent')), ensure_ascii=format_json_ascii)


@registries.Registry.formats('csv-with-header')
@registries.Registry.formats('csvh')
@registries.Registry.formats('csv')
def _format_csv(record: Union[list, dict]) -> str:
    """formats the values of the record as comma separated values  """
    if isinstance(record, list):
        lines = [_csv_line(item) for item in record]
        return '\n'.join(lines)
    return _csv_line(record)


def _csv_line(record):
    return ','.join([str(val) for val in record.values()])


@registries.Registry.formats('yaml')
def _format_yaml(record: Union[list, dict]) -> str:
    """formats the values of the record as YAML """
    return str(yaml.dump(record, sort_keys=False, width=4096)).strip()


class WriterInterface(ABC):
    """Interface for classes that write the generated values out"""

    @abstractmethod
    def write(self, value):
        """Write the value to the configured output destination

        Args:
            value: to write
        """


def single_field(writer: WriterInterface, output_key: bool):
    """
    Creates a OutputHandler field level events

    Args:
        writer (WriterInterface): to write the processed records
        output_key: if the key should be output along with the value

    Returns:
        OutputHandlerInterface
    """
    return _SingleFieldOutput(writer, output_key)


class _SingleFieldOutput(OutputHandlerInterface):
    """Writes each field as it is created"""

    def __init__(self, writer: WriterInterface, output_key: bool):
        self.writer = writer
        self.output_key = output_key

    def handle(self, key, value):
        if self.output_key:
            self.writer.write(f'{key} -> {value}')
        else:
            self.writer.write(str(value))

    def finished_record(self, iteration=None, group_name=None, exclude_internal=False):
        pass

    def finished_iterations(self):
        pass


def record_level(record_processor: RecordProcessor,
                 writer: WriterInterface,
                 records_per_file: int = 1) -> OutputHandlerInterface:
    """
    Creates a OutputHandler for record level events

    Args:
        record_processor: to process the records into strings
        writer: to write the processed records
        records_per_file: number of records to accumulate before writing

    Returns:
        OutputHandlerInterface
    """
    return _RecordLevelOutput(record_processor, writer, records_per_file)


class _RecordLevelOutput(OutputHandlerInterface):
    """Class that outputs after all fields have been generated"""

    def __init__(self, record_processor, writer, records_per_file):
        self.record_processor = record_processor
        self.writer = writer
        self.records_per_file = records_per_file
        self.current = {}
        self.buffer = []

    def handle(self, key, value):
        self.current[key] = value

    def finished_record(self, iteration, group_name, exclude_internal=False):
        current = self.current
        if not exclude_internal:
            current['_internal'] = {
                '_iteration': iteration,
                '_field_group': group_name
            }
        if self.records_per_file == 1:
            processed = self.record_processor.process(current)
            self.writer.write(processed)
            self.current.clear()
        else:
            self.buffer.append(current.copy())
            self.current.clear()
            if len(self.buffer) == self.records_per_file:
                processed = self.record_processor.process(self.buffer)
                self.writer.write(processed)
                self.buffer.clear()

    def finished_iterations(self):
        if len(self.buffer) == 0:
            return
        processed = self.record_processor.process(self.buffer)
        self.writer.write(processed)
        self.buffer.clear()


def stdout_writer() -> WriterInterface:
    """Creates a WriterInterface that writes results to stdout

    Returns:
        writer that writes to stdout
    """
    return _StdOutWriter()


class _StdOutWriter(WriterInterface):
    """Writes values to stdout"""

    def write(self, value: str):
        print(value)


def suppress_output_writer() -> WriterInterface:
    """ Returns a writer that suppresses the output to stdout """
    return _SuppressOutput()


class _SuppressOutput(WriterInterface):
    """ Suppresses output """

    def write(self, value):
        pass


def single_file_writer(outdir: str, outname: str, overwrite: bool) -> WriterInterface:
    """Creates a Writer for a single output file

    Args:
        outdir: output directory
        outname: output file name
        overwrite: if should overwrite exiting output files

    Returns:
        Writer for a single file
    """
    return _SingleFileWriter(outdir, outname, overwrite)


class _SingleFileWriter(WriterInterface):
    """Writes all values to same file"""

    def __init__(self, outdir: str, outname: str, overwrite: bool):
        self.outdir = outdir
        self.outname = outname
        self.overwrite = overwrite

    def write(self, value):
        outfile = os.path.join(self.outdir, self.outname)
        if self.overwrite:
            mode = 'w'
        else:
            mode = 'a'
        with open(outfile, mode, encoding='utf-8') as handle:
            handle.write(value)
            handle.write('\n')
        _log.info('Wrote data to %s', outfile)


def incrementing_file_writer(outdir: str,
                             engine: RecordProcessor) -> WriterInterface:
    """Creates a WriterInterface that increments the count in the file name once records_per_file have been written

    Args:
        outdir: output directory
        engine: to generate file names with

    Returns:
        a Writer that increments the a count in the file name
    """
    return _IncrementingFileWriter(outdir, engine)


class _IncrementingFileWriter(WriterInterface):
    """Writes processed output to disk and increments the file name with a count"""

    def __init__(self, outdir, engine: RecordProcessor):
        self.outdir = outdir
        self.engine = engine
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.count = 0

    def write(self, value):
        outfile = os.path.join(self.outdir, self.engine.process({'count': self.count}))
        self.count += 1
        with open(outfile, 'w', encoding='utf-8') as handle:
            handle.write(value)
            handle.write('\n')
        _log.info('Wrote data to %s', outfile.replace('/', os.path.sep))


class _FormatProcessor(RecordProcessor):
    """A simple class that wraps a record formatting function"""

    def __init__(self, key: str):
        self.format_func = registries.Registry.formats.get(key)

    def process(self, record: Union[list, dict]) -> str:
        """
        Processes the given record into the appropriate output string

        Args:
            record: dictionary of record to format

        Returns:
            The formatted record
        """
        return self.format_func(record)


class _CsvFormatProcessor(RecordProcessor):
    """for extra csv formatting """

    def __init__(self, key: str, add_header: bool = False):
        self.format_func = registries.Registry.formats.get(key)
        self.add_header = add_header
        self.header_added = False

    def process(self, record: Union[list, dict]) -> str:
        """
        Processes the given record into the appropriate output string

        Args:
            record: dictionary of record to format

        Returns:
            The formatted record
        """
        if self.add_header and not self.header_added:
            if isinstance(record, list):
                header = {k: k for k, _ in record[0].items()}
            else:
                header = {k: k for k, _ in record.items()}
            return '\n'.join([self.format_func(header), self.format_func(record)])
        return self.format_func(record)


def _for_format(key: str) -> RecordProcessor:
    """
    Creates FormatProcessor for provided key if one is registered

    Args:
        key: for formatter

    Returns:
        The FormatProcessor for the given key

    Raises:
        SpecException when key is not registered
    """
    try:
        if key.startswith('csv'):
            return _CsvFormatProcessor(key, key in ['csv-with-header', 'csvh'])
        return _FormatProcessor(key)
    except catalogue.RegistryError as err:
        raise SpecException(str(err)) from err


def processor(template: Union[str, Path, None] = None,
              format_name: Union[str, None] = None) -> Union[None, RecordProcessor]:
    """
    Configures the record level processor for either the template or for the format_name

    Args:
        template: path to template or template as string
        format_name: one of the valid registered formatter names

    Returns:
        RecordProcessor if valid template of format_name provide, None otherwise

    Raises:
        SpecException when format_name is not registered or if both template and format specified

    Examples:
        >>> import datacraft
        >>> engine = datacraft.outputs.processor(template='/path/to/template.jinja')
        >>> engine = datacraft.outputs.processor(template='{{ Inline: {{ variable }}')
        >>> formatter = datacraft.outputs.processor(format_name='json')
        >>> formatter = datacraft.outputs.processor(format_name='my_custom_registered_format')
    """
    if template and format_name:
        raise SpecException('Only one of template or format_name should be supplied')
    # so name doesn't shadow
    _processor = None
    if template:
        _log.debug('Using template: %s', template)
        if os.path.exists(template):
            _processor = template_engines.for_file(template)
        elif '{{' in template:  # type: ignore
            _processor = template_engines.string(template)  # type: ignore
        else:
            raise SpecException(f'Unable to determine how to handle template {template}, with type: {type(template)}')
    elif format_name:
        _log.debug('Using %s formatter for output', format_name)
        _processor = _for_format(format_name)

    return _processor


def get_writer(outdir: Union[str, None] = None,
               outfile: Union[str, None] = None,
               overwrite: bool = False,
               **kwargs) -> WriterInterface:
    """
    creates the appropriate output writer from the given args and params

    If no output directory is specified/configured will write to stdout

    Args:
        outdir: Directory to write output to
        outfile: If a specific file should be used for the output, default is to construct the name from kwargs
        overwrite: Should existing files with the same name be overwritten

    Keyword Args:
        outfile_prefix: the prefix of the output files i.e. test-data-
        extension: to append to the file name prefix i.e. .csv
        suppress_output: if output to stdout should be suppressed, only valid if outdir is None

    Returns:
        The configured Writer

    Examples:
        >>> import datacraft
        >>> csv_writer = datacraft.outputs.get_writer('./output', outfileprefix='test-data-', extension='.csv')
    """
    if outdir:
        _log.debug('Creating output file writer for dir: %s, prefix: %s', outdir, kwargs.get('outfile_prefix'))
        if outfile:
            writer = single_file_writer(
                outdir=outdir,
                outname=outfile,
                overwrite=overwrite
            )
        else:
            prefix = kwargs.get('outfile_prefix', registries.get_default('outfile_prefix'))
            extension = kwargs.get('extension', registries.get_default('outfile_extension'))
            engine = file_name_engine(prefix, extension)
            writer = incrementing_file_writer(
                outdir=outdir,
                engine=engine
            )
    else:
        if kwargs.get('suppress_output'):
            writer = suppress_output_writer()
        else:
            _log.debug('Writing output to stdout')
            writer = stdout_writer()
    return writer


def file_name_engine(prefix: str, extension: str) -> RecordProcessor:
    """
    creates a templating engine that will produce file names based on the count

    Args:
        prefix: prefix for file name
        extension: suffix for file name

    Returns:
        template engine for producing file names
    """
    template_str = prefix + "-{{count}}" + extension
    engine = template_engines.string(template_str)
    return engine
