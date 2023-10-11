"""Main function for cli datacraft inference"""
import argparse
import json
import logging
import os
import sys

import datacraft.infer

_log = logging.getLogger(__name__)
_LOG_LEVELS = [
    "critical",
    "fatal",
    "error",
    "warning",
    "warn",
    "info",
    "debug",
    "off",
    "stop",
    "disable"
]


def process_file(filepath, filetype, args):
    if filetype == "json":
        with open(filepath, 'r', encoding='utf-8') as fp:
            records = json.load(fp)
        if not isinstance(records, list):
            records = [records]
        return datacraft.infer.from_examples(records,
                                             limit=args.limit,
                                             limit_weighted=args.limit_weighted,
                                             duplication_threshold=args.duplication_threshold)
    elif filetype == "csv":
        return datacraft.infer.csv_to_spec(filepath,
                                           limit=args.limit,
                                           limit_weighted=args.limit_weighted,
                                           duplication_threshold=args.duplication_threshold)
    else:
        raise ValueError(f"Unsupported file type: {filetype}")


def wrap_main():
    """wraps main with try except for SpecException """
    try:
        main(sys.argv[1:])
    except Exception as exc:
        _log.error(str(exc))


def main(argv):
    """Runs the tool """
    parser = argparse.ArgumentParser(description="Infer Data Spec from given CSV or JSON sample data.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--csv', help='Path to CSV file', type=str)
    group.add_argument('--json', help='Path to JSON file', type=str)
    group.add_argument('--csv-dir', help='Directory path containing CSV files', type=str)
    group.add_argument('--json-dir', help='Directory path containing JSON files', type=str)
    parser.add_argument('--output', help='Output file to write results', type=str)
    parser.add_argument('--limit', dest='limit', type=int, default=0,
                        help='Max size of lists or weighted values to populate when unable to infer a more specific '
                             'type from data')
    parser.add_argument('--limit-weighted', dest='limit_weighted', action='store_true',
                        help='If weighted values are to be created, take top limit weights')
    parser.add_argument("-dt", "--duplication-threshold", dest='duplication_threshold',
                        type=valid_range,
                        default=0.2,
                        help="Duplication ratio above which the lists of values are considered significantly "
                             "duplicated. Value should be between 0 and 1 (inclusive). Measures the ratio of unique "
                             "items to total items")
    parser.add_argument('-l', '--log-level', dest='log_level', default="info", choices=_LOG_LEVELS,
                        help='Logging level verbosity, default is info')
    args = parser.parse_args(argv)

    files_to_process = []

    _configure_logging(args.log_level)
    if args.csv:
        _log.info("Processing %s...", args.csv)
        files_to_process.append((args.csv, "csv"))
    elif args.json:
        _log.info("Processing %s...", args.json)
        files_to_process.append((args.json, "json"))
    elif args.csv_dir:
        _log.info("Processing CSVs from %s...", args.csv_dir)
        for filename in os.listdir(args.csv_dir):
            files_to_process.append((os.path.join(args.csv_dir, filename), "csv"))
    elif args.json_dir:
        _log.info("Processing JSONs from %s...", args.json_dir)
        for filename in os.listdir(args.json_dir):
            files_to_process.append((os.path.join(args.json_dir, filename), "json"))

    results = {}
    for filepath, filetype in files_to_process:
        result = process_file(filepath, filetype, args)
        if result is None:
            continue
        results.update(result)

    if args.output:
        with open(args.output, 'w') as outfile:
            json.dump(results, outfile, indent=4)
    else:
        print(json.dumps(results, indent=4))


def valid_range(arg):
    try:
        value = float(arg)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid float value: {arg}")
    if 0 <= value <= 1:
        return value
    else:
        raise argparse.ArgumentTypeError(f"Value {arg} is out of range [0, 1]")


def _configure_logging(loglevel):
    if str(loglevel).lower() in ['off', 'stop', 'disable']:
        logging.disable(logging.CRITICAL)
    else:
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {loglevel}')
        logging.basicConfig(
            format='%(levelname)s [%(asctime)s] %(message)s',
            level=numeric_level,
            datefmt='%d-%b-%Y %I:%M:%S %p'
        )


if __name__ == "__main__":
    main(sys.argv[1:])
