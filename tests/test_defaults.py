import datagen


@datagen.registry.defaults('dino')
def _get_default_dinosaur():
    return 'velociraptor'


def test_default_registry():
    assert datagen.registries.get_default('dino') == 'velociraptor'


def test_default_registry_set():
    datagen.registries.set_default('dino', 'triceratops')

    assert datagen.registries.get_default('dino') == 'triceratops'


def test_default_registry_get_all():
    defaults = datagen.registries.all_defaults()
    assert type(defaults) == dict
    assert len(defaults) > 0
