import pytest

from ophbench.models.base import BaseModelAdapter
from ophbench.models.errors import AdapterNotImplementedError
from ophbench.models.factory import AdapterFactory


class DummyAdapter(BaseModelAdapter):
    model_id = "dummy"
    capabilities = ("image_encoding",)

    def check_environment(self):
        return []

    def load(self):
        return self


def test_dummy_adapter_can_be_registered_and_created():
    factory = AdapterFactory()
    factory.register(DummyAdapter)
    assert isinstance(factory.create("dummy"), DummyAdapter)


def test_unimplemented_adapter_error_contains_context():
    factory = AdapterFactory(registry_root="registry")
    with pytest.raises(AdapterNotImplementedError) as exc:
        factory.create("retfound")
    message = str(exc.value)
    assert "retfound" in message
    assert "phase1_image_encoder" in message
    assert "implemented" in message
