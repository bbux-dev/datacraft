import argparse
import json

from datacraft import template_engines


def main():
    with open('raw_examples.json', 'r') as handle:
        record = json.load(handle)
    engine = template_engines.for_file('types/calculate.rst')
    print(engine.process(record))


if __name__ == '__main__':
    main()
