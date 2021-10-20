"""
Module holds output related classes and functions
"""
from typing import Any
from abc import ABC, abstractmethod
import os
import json
import logging
import catalogue  # type: ignore
import datagen
from .types import registry

log = logging.getLogger(__name__)


@datagen.registry.formats('json')
def _format_json(record: dict) -> str:
    """formats the record as compressed json  """
    return json.dumps(record)


@datagen.registry.formats('json-pretty')
def _format_json_pretty(record: dict) -> str:
    """pretty prints the record as json  """
    return json.dumps(record, indent=int(datagen.types.get_default('json_indent')))


@datagen.registry.formats('csv')
def _format_csv(record: dict) -> str:
    """formats the values of the record as comma separated values  """
    return ','.join([str(val) for val in record.values()])


class OutputHandlerInterface(ABC):
    """Interface four handling generated output values"""

    @abstractmethod
    def handle(self, key: str, value: Any):
        """This is called each time a new value is generated for a given field

        Args:
            key: the field name
            value: the new value for the field
        """

    @abstractmethod
    def finished_record(self,
                        iteration: int,
                        group_name: str,
                        exclude_internal: bool = False):
        """This is called whenever all of the fields for a record have been generated for one iteration

        Args:
            iteration: iteration we are on
            group_name: group this record is apart of
            exclude_internal: if external fields should be excluded from output record
        """


class WriterInterface(ABC):
    """Interface for classes that write the generated values out"""

    @abstractmethod
    def write(self, value):
        """Write the value to the configured output destination

        Args:
            value: to write
        """


class SingleFieldOutput(OutputHandlerInterface):
    """Writes each field as it is created"""

    def __init__(self, writer: WriterInterface, output_key):
        self.writer = writer
        self.output_key = output_key

    def handle(self, key, value):
        if self.output_key:
            self.writer.write('%s -> %s' % (key, value))
        else:
            self.writer.write(value)

    def finished_record(self, iteration=None, group_name=None, exclude_internal=False):
        pass


class RecordLevelOutput(OutputHandlerInterface):
    """Class to output after all fields have been generated"""

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
    return StdOutWriter()


class StdOutWriter(WriterInterface):
    """Writes values to stdout"""

    def write(self, value: str):
        print(value)


def single_file_writer(outdir: str, outname: str, overwrite: bool) -> WriterInterface:
    """Creates a Writer for a single output file

    Args:
        outdir: output directory
        outname: output file name
        overwrite: if should overwrite exiting output files

    Returns:
        Writer for a single file
    """
    return SingleFileWriter(outdir, outname, overwrite)


class SingleFileWriter(WriterInterface):
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
    """Creates a WriterInterface that increments the a count in the file name

    Args:
        outdir: output directory
        outname: output file name
        extension: to append to the file i.e. csv
        records_per_file: number of records to write before a new file is opened

    Returns:
        a Writer that increments the a count in the file name
    """
    return IncrementingFileWriter(outdir, outname, extension, records_per_file)


class IncrementingFileWriter(WriterInterface):
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


class FormatProcessor:
    """A simple class that wraps a record formatting function"""

    def __init__(self, key):
        self.format_func = registry.formats.get(key)

    def process(self, record: dict) -> str:
        """
        Processes the given record into the appropriate output string
        Args:
            record: dictionary of record to format

        Returns:
            The formatted record
        """
        return self.format_func(record)


def for_format(key: str) -> FormatProcessor:
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
        return FormatProcessor(key)
    except catalogue.RegistryError as err:
        raise datagen.SpecException(str(err))
