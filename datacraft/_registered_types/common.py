"""module for shared code for datacraft registry functions"""
from contextlib import redirect_stdout
import io
import json

import datacraft


def build_suppliers_map(field_spec: dict, loader: datacraft.Loader) -> dict:
    """uses refs or fields to build a map for those suppliers"""
    if 'refs' not in field_spec and 'fields' not in field_spec:
        raise datacraft.SpecException(f'Must define one of fields or refs. {json.dumps(field_spec)}')
    if 'refs' in field_spec and 'fields' in field_spec:
        raise datacraft.SpecException(f'Must define only one of fields or refs. {json.dumps(field_spec)}')
    mappings = _get_mappings(field_spec, 'refs')
    mappings.update(_get_mappings(field_spec, 'fields'))
    if len(mappings) < 1:
        raise datacraft.SpecException(f'fields or refs empty: {json.dumps(field_spec)}')
    suppliers_map = {}
    for field_or_ref, alias in mappings.items():
        supplier = loader.get(field_or_ref)
        suppliers_map[alias] = supplier
    return suppliers_map


def _get_mappings(field_spec, lookup_key):
    """ retrieve the field aliasing for the given key, refs or fields """
    mappings = field_spec.get(lookup_key, [])
    if isinstance(mappings, list):
        mappings = {_key: _key for _key in mappings}
    return mappings


def standard_example_usage(example: dict, num: int, pretty: bool = False, no_reformat: bool = False):
    """ builds map for cli and api usage """
    return {
        "cli": standard_cli_example_usage(example, num, pretty, no_reformat),
        "api": standard_api_example_usage(example, num, no_reformat)
    }


def standard_cli_example_usage(example: dict, num: int, pretty: bool = False, no_reformat: bool = False):
    """builds a single usage from given example spec"""
    if no_reformat:
        formatted_spec = example  # type: ignore
    else:
        formatted_spec = datacraft.preprocess_and_format(example)  # type: ignore
    datacraft_format = 'json-pretty' if pretty else 'json'
    command = f'$ datacraft -s spec.json -i {num} --format {datacraft_format} -x -l off'
    if pretty:
        output = json.dumps(datacraft.entries(example, num, enforce_schema=True), indent=4)
    else:
        output = json.dumps(
            datacraft.entries(example, num, enforce_schema=True),
            ensure_ascii=datacraft.registries.get_default('format_json_ascii'))
    return f'Example Spec:\n{formatted_spec}\n\n{command}\n{output}\n'


def standard_api_example_usage(example: dict, num: int, no_reformat: bool = False):
    """builds a single usage from given example spec"""
    if no_reformat:
        formatted_spec = str(example)  # type: ignore
    else:
        formatted_spec = datacraft.preprocess_and_format(example)  # type: ignore
    # need to make spec python friendly
    formatted_spec = formatted_spec.replace('true', 'True')
    formatted_spec = formatted_spec.replace('false', 'False')
    formatted_spec = formatted_spec.replace('null', 'None')

    template = '''
import datacraft

spec = __SPEC__

print(*datacraft.entries(spec, __N__), sep='\\n')
    '''
    code = template.replace('__SPEC__', formatted_spec).replace('__N__', str(num))

    f = io.StringIO()
    with redirect_stdout(f):
        exec(code)
    output = f.getvalue()

    return f'API Example:\n{code}\n{output}\n'
