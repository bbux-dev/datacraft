import pytest

import datacraft._registered_types.entrypoint


@pytest.fixture(scope="session", autouse=True)
def setup(request):
    # since these may not be installed yet
    datacraft._registered_types.entrypoint.load_custom()
