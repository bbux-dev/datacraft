"""Main function for cli datacraft inference"""
import argparse
import json
import logging
import os
import sys

import datacraft.infer

_log = logging.getLogger(__name__)


def process_file(filepath, filetype):
    if filetype == "json":
        with open(filepath, 'r', encoding='utf-8') as fp:
            records = json.load(fp)
        if not isinstance(records, list):
            records = [records]
        return datacraft.infer.from_examples(records)
    elif filetype == "csv":
        return datacraft.infer.csv_to_spec(filepath)
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
    parser = argparse.ArgumentParser(description="Process CSV or JSON data.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--csv', help='Path to CSV file', type=str)
    group.add_argument('--json', help='Path to JSON file', type=str)
    group.add_argument('--csv-dir', help='Directory path containing CSV files', type=str)
    group.add_argument('--json-dir', help='Directory path containing JSON files', type=str)
    parser.add_argument('--output', help='Output file to write results', type=str)

    args = parser.parse_args(argv)

    files_to_process = []

    if args.csv:
        files_to_process.append((args.csv, "csv"))
    elif args.json:
        files_to_process.append((args.json, "json"))
    elif args.csv_dir:
        for filename in os.listdir(args.csv_dir):
            if filename.endswith('.csv'):
                files_to_process.append((os.path.join(args.csv_dir, filename), "csv"))
    elif args.json_dir:
        for filename in os.listdir(args.json_dir):
            if filename.endswith('.json'):
                files_to_process.append((os.path.join(args.json_dir, filename), "json"))

    results = []
    for filepath, filetype in files_to_process:
        result = process_file(filepath, filetype)
        if result is None:
            continue
        results.append(result)

    if args.output:
        with open(args.output, 'w') as outfile:
            for result in results:
                outfile.write(result + "\n")
    else:
        for result in results:
            print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main(sys.argv)
