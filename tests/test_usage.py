import pytest
import datacraft

USAGE_MESSAGE = 'Usage For Test Only!!!'

DEMO_FOR_TEST = 'demo-for-test'
DEMO_FOR_TEST_NO_CLI_USAGE_DEFINED = 'demo-for-test-no-usage'


@datacraft.registry.types(DEMO_FOR_TEST)
def _test_supplier(_, __):
    return None


@datacraft.registry.usage(DEMO_FOR_TEST)
def _test_usage():
    return {'cli': USAGE_MESSAGE, 'api': USAGE_MESSAGE}


@datacraft.registry.types(DEMO_FOR_TEST_NO_CLI_USAGE_DEFINED)
def _test_supplier_no_usage(_, __):
    return None


@datacraft.registry.usage(DEMO_FOR_TEST_NO_CLI_USAGE_DEFINED)
def _test_usage_api_only():
    return {"api": "import datacraft\n#..."}


def test_usage_misspelled_type():
    usage_string = datacraft.usage.build_cli_help(DEMO_FOR_TEST + 'zzz')
    assert DEMO_FOR_TEST + 'zzz' in usage_string
    assert 'unknown type' in usage_string


def test_usage_no_filter():
    usage_string = datacraft.usage.build_cli_help()
    assert DEMO_FOR_TEST in usage_string
    assert USAGE_MESSAGE in usage_string
    assert f'{DEMO_FOR_TEST_NO_CLI_USAGE_DEFINED} | no cli usage defined' in usage_string


def test_api_usage_no_filter():
    usage_string = datacraft.usage.build_api_help()
    assert DEMO_FOR_TEST_NO_CLI_USAGE_DEFINED in usage_string


def test_usage_constrained():
    usage_string = datacraft.usage.build_cli_help(DEMO_FOR_TEST, DEMO_FOR_TEST_NO_CLI_USAGE_DEFINED)
    assert DEMO_FOR_TEST in usage_string
    assert USAGE_MESSAGE in usage_string
    assert f'{DEMO_FOR_TEST_NO_CLI_USAGE_DEFINED} | no cli usage defined' in usage_string


@pytest.mark.parametrize("key", datacraft.registries.registered_types())
def test_exercise_all_keys(key):
    assert key in datacraft.usage.build_cli_help(key)
    assert key in datacraft.usage.build_api_help(key)
