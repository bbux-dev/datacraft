#!/bin/env python
"""
Utility to build data structures for SCHEMAS.md
"""
import os
import glob
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    paths = glob.glob('../../datagen/schema/*.schema.json')
    schemas = []
    with open('../../datagen/schema/definitions.json') as handle:
        schema = handle.read()
    schemas.append({
        'tag': 'definitions',
        'title': 'Definitions',
        'schema': schema
    })
    for path in paths:
        basename = os.path.basename(path)
        tag = basename.replace('.schema.json', '')
        title = tag
        type_names = title
        if type_names == 'date':
            title = 'Date types (data, date.iso, date.iso.us)'
            type_names = 'date, date.iso, date.iso.us'
        if type_names == 'ip':
            title = 'IP types (ip, ipv4)'
            type_names = 'ip, ipv4'
        if type_names == 'range':
            title = 'Range types (range, rand_range)'
            type_names = 'range, rand_range'
        with open(path) as handle:
            schema = handle.read()
        schemas.append({
            'tag': tag,
            'title': title,
            'type_names': type_names,
            'schema': schema
        })

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('SCHEMAS.jinja.md')
    print(template.render({'schemas': schemas}))


if __name__ == '__main__':
    main()
