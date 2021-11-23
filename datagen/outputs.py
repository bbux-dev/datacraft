"""
Module holds output related classes and functions
"""
from typing import Union
from abc import ABC, abstractmethod
import os
import json
import logging
import catalogue  # type: ignore
from pathlib import Path
import datagen
from . import template_engines, types
from .model import RecordProcessor, OutputHandlerInterface
from .exceptions import SpecException

log = logging.getLogger(__name__)


@datagen.registry.formats('json')
def _format_json(record: dict) -> str:
    """formats the record as compressed json  """
    return json.dumps(record)


@datagen.registry.formats('json-pretty')
def _format_json_pretty(record: dict) -> str:
    """pretty prints the record as json  """
    return json.dumps(record, indent=int(types.get_default('json_indent')))


@datagen.registry.formats('csv')
def _format_csv(record: dict) -> str:
    """formats the values of the record as comma separated values  """
    return ','.join([str(val) for val in record.values()])


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
            self.writer.write('%s -> %s' % (key, value))
        else:
            self.writer.write(value)

    def finished_record(self, iteration=None, group_name=None, exclude_internal=False):
        pass


def record_level(record_processor: RecordProcessor, writer: WriterInterface) -> OutputHandlerInterface:
    """
    Creates a OutputHandler for record level events

    Args:
        record_processor (RecordProcessor): to process the records into strings
        writer (WriterInterface): to write the processed records

    Returns:
        OutputHandlerInterface
    """
    return _RecordLevelOutput(record_processor, writer)


class _RecordLevelOutput(OutputHandlerInterface):
    """Class that outputs after all fields have been generated"""

    def __init__(self, record_processor, writer):
        self.record_processor = record_processor
        self.writer = writer
        self.current = {}

    def handle(self, key, value):
        self.current[key] = value

    def finished_record(self, iteration, group_name, exclude_internal=False):
        current = self.current
        if not exclude_internal:
            current['_internal'] = {
                '_iteration': iteration,
                '_field_group': group_name
            }
        processed = self.record_processor.process(current)
        self.writer.write(processed)
        self.current.clear()


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
        with open(outfile, mode) as handle:
            handle.write(value)
            handle.write('\n')
        log.info('Wrote data to %s', outfile)


def incrementing_file_writer(outdir: str,
                             outname: str,
                             extension: str = None,
                             records_per_file: int = 1) -> WriterInterface:
    """Creates a WriterInterface that increments the count in the file name once records_per_file have been written

    Args:
        outdir: output directory
        outname: output file name
        extension: to append to the file i.e. .csv
        records_per_file: number of records to write before a new file is opened

    Returns:
        a Writer that increments the a count in the file name
    """
    return _IncrementingFileWriter(outdir, outname, extension, records_per_file)


class _IncrementingFileWriter(WriterInterface):
    """Writes processed output to disk and increments the file name with a count"""

    def __init__(self, outdir, outname, extension=None, records_per_file=1):
        self.outdir = outdir
        self.outname = outname
        self.extension = extension
        if self.extension and not extension.startswith('.'):
            self.extension = '.' + extension
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.count = 0
        self.records_per_file = records_per_file
        self.record_count = 0

    def write(self, value):
        extension = self.extension if self.extension else ''
        outfile = '%s/%s-%d%s' % (self.outdir, self.outname, self.count, extension)
        if self.record_count == 0:
            mode = 'w'
        else:
            mode = 'a'
        with open(outfile, mode) as handle:
            handle.write(value)
            handle.write('\n')
        self.record_count += 1
        if self.record_count == self.records_per_file:
            self.record_count = 0
            self.count += 1


class _FormatProcessor(RecordProcessor):
    """A simple class that wraps a record formatting function"""

    def __init__(self, key):
        self.format_func = types.registry.formats.get(key)

    def process(self, record: dict) -> str:
        """
        Processes the given record into the appropriate output string

        Args:
            record: dictionary of record to format

        Returns:
            The formatted record
        """
        return self.format_func(record)


def _for_format(key: str) -> _FormatProcessor:
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
        return _FormatProcessor(key)
    except catalogue.RegistryError as err:
        raise SpecException(str(err))


def processor(template: Union[str, Path] = None, format_name: str = None) -> Union[None, RecordProcessor]:
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
        >>> import datagen
        >>> processor = datagen.outputs.processor(template='/path/to/template.jinja')
        >>> processor = datagen.outputs.processor(template='{{ Inline: {{ variable }}')
        >>> processor = datagen.outputs.processor(format_name='json')
        >>> processor = datagen.outputs.processor(format_name='my_custom_registered_format')
    """
    if template and format_name:
        raise SpecException('Only one of template or format_name should be supplied')
    processor = None
    if template:
        log.debug('Using template: %s', template)
        if os.path.exists(template):
            processor = template_engines.for_file(template)
        elif '{{' in template:  # type: ignore
            processor = template_engines.string(template)  # type: ignore
        else:
            raise SpecException(f'Unable to determine how to handle template {template}, with type: {type(template)}')
    elif format_name:
        log.debug('Using %s formatter for output', format_name)
        processor = _for_format(format_name)

    return processor


def get_writer(outdir: str = None,
               outfile: str = None,
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
        outfileprefix: the prefix of the output files i.e. test-data-
        extension: to append to the file name prefix i.e. .csv
        recordsperfile: how many records per file to write
        suppress_output: if output to stdout should be suppressed, only valid if outdir is None

    Returns:
        The configured Writer

    Examples:
        >>> import datagen
        >>> writer = datagen.outputs.get_writer('./output', outfileprefix='test-data-', extension='.csv')
    """
    if outdir:
        log.debug('Creating output file writer for dir: %s', outdir)
        if outfile:
            writer = single_file_writer(
                outdir=outdir,
                outname=outfile,
                overwrite=overwrite
            )
        else:
            writer = incrementing_file_writer(
                outdir=outdir,
                outname=kwargs.get('outfileprefix', types.get_default('outfileprefix')),
                extension=kwargs.get('extension'),
                records_per_file=kwargs.get('recordsperfile', 1)
            )
    else:
        if kwargs.get('suppress_output'):
            writer = suppress_output_writer()
        else:
            log.debug('Writing output to stdout')
            writer = stdout_writer()
    return writer

