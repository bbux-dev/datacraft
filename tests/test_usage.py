import datacraft
import datacraft.usage

USAGE_MESSAGE = 'Usage For Test Only!!!'

DEMO_FOR_TEST = 'demo-for-test'
DEMO_FOR_TEST_NO_USAGE_DEFINED = 'demo-for-test-no-usage'


@datacraft.registry.types(DEMO_FOR_TEST)
def _test_supplier(_, __):
    return None


@datacraft.registry.usage(DEMO_FOR_TEST)
def _test_usage():
    return USAGE_MESSAGE


@datacraft.registry.types(DEMO_FOR_TEST_NO_USAGE_DEFINED)
def _test_supplier_no_usage(_, __):
    return None


def test_usage_misspelled_type():
    usage_string = datacraft.usage.build_cli_help([DEMO_FOR_TEST + 'zzz'])
    assert DEMO_FOR_TEST + 'zzz' in usage_string
    assert 'unknown type' in usage_string


def test_usage_no_filter():
    usage_string = datacraft.usage.build_cli_help()
    assert DEMO_FOR_TEST in usage_string
    assert USAGE_MESSAGE in usage_string
    assert f'{DEMO_FOR_TEST_NO_USAGE_DEFINED} | no usage defined' in usage_string


def test_usage_constrained():
    usage_string = datacraft.usage.build_cli_help([DEMO_FOR_TEST, DEMO_FOR_TEST_NO_USAGE_DEFINED])
    assert DEMO_FOR_TEST in usage_string
    assert USAGE_MESSAGE in usage_string
    assert f'{DEMO_FOR_TEST_NO_USAGE_DEFINED} | no usage defined' in usage_string
