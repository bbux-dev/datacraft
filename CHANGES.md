v0.3.1
------

* Fix for custom types not loading when datacraft used programmatically.
* Addition of `datacraft.entries` function for quickly generating records from a given spec

```python
import datacraft

spec = {
   "super_power": {
      "type": "values",
      "config": { "sample": True },
      "data": {
         "fast reader": 0.5,
         "wordle expert": 0.4,
         "super strength": 0.05,
         "super speed": 0.01,
         "invisibility": 0.01,
         "indestructible": 0.01,
         "laser eyes": 0.01,
         "teleportation": 0.00000000001
      }
   }
}
records = datacraft.entries(spec, 5)
```

v0.3.0
------
* Introduced `datacraft.custom_type_loader` entrypoint for discovering and loading `@datacraft.registry.*` functions.

Add to setup.cfg:

```yaml
[options.entry_points]
datacraft.custom_type_loader =
    mycustomstuff = mypackage:load_custom
```

See [custom-types-entry-point](https://datacraft.readthedocs.io/en/latest/usage.html#custom-types-entry-point) for
details

v0.2.1
------
* Added typing support to ``csv_select`` field definitions: i.e.
```json
{
   "multiple_csv_fields": {
      "type": "csv_select",
      "data": {
         "one:float": 1,
         "tre": 3,
         "svn": {"col": 7, "cast": "int"}
      },
      "config": {"datafile": "{{ input_csv }}"}
   }
}
```
* Fixes for GeoJSON example documentation

v0.2.0
------

 * Added new `templated` type 
(see [templated type](https://datacraft.readthedocs.io/en/latest/coretypes.html#templated)) e.g:
```json
{"filled_in": {"type":  "templated", "data": "{{one}} and {{two}} and a ...", "refs": ["one", "two"]}}
```
 * Expanded API for suppliers module. Most core types have an analog function in the suppliers module to create a value 
   supplier. e.g:
```python
from datacraft import suppliers
supplier_map = { 'char': suppliers.values(['a', 'b', 'c']), 'num': suppliers.values([1, 2, 3]) }
template_str = 'letter {{ char }}, number {{ num }}'
supplier = suppliers.templated(supplier_map, template_str)
supplier.next(0)  # -> letter a, number 1
```
 * Records now returned as list by default, so `--records-per-file` or `-r` dictates the size of this list e.g:
```shell
# outputs 10 total records with two per file as a list
datacraft --inline '{foo:date.iso: {}}' --format json-pretty -x --log-level off -i 10 -r 2 -o . -p demo -e .json
ls
demo-0.json  demo-1.json  demo-2.json  demo-3.json  demo-4.json
cat demo-0.json
[
    {
        "foo": "2022-02-01T17:17:58"
    },
    {
        "foo": "2022-02-14T19:56:45"
    }
]
```
 * Migrated from travis-ci to circle-ci for builds
 * Lots of bug fixes and code cleanup

v0.1.0
------

 * Initial Release