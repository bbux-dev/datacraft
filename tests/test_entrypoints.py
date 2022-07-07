import importlib_metadata

import datacraft.entrypoints


def test_bad_entry_point(mocker):
    def bad_load_func():
        raise Exception('woopsie')

    class EntryPoint:
        name = 'test'

        def load(self):
            return bad_load_func

    mocker.patch('importlib_metadata.EntryPoints.select', return_value=[EntryPoint()])
    # for coverage
    datacraft.entrypoints.load_eps()
