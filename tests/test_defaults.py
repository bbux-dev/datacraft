import datacraft


@datacraft.registry.defaults('dino')
def _get_default_dinosaur():
    return 'velociraptor'


def test_default_registry():
    assert datacraft.registries.get_default('dino') == 'velociraptor'


def test_default_registry_set():
    datacraft.registries.set_default('dino', 'triceratops')

    assert datacraft.registries.get_default('dino') == 'triceratops'


def test_default_registry_get_all():
    defaults = datacraft.registries.all_defaults()
    assert type(defaults) == dict
    assert len(defaults) > 0
