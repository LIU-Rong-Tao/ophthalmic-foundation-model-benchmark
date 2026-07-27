from pathlib import Path

from ophbench.registry.loader import load_registry

from .errors import AdapterNotImplementedError


class AdapterFactory:
    def __init__(self, registry_root=None):
        self._adapters = {}
        self.registry_root = Path(registry_root) if registry_root else None

    def register(self, adapter_type):
        checkpoint_id = getattr(adapter_type, "checkpoint_id", None)
        self._adapters[(adapter_type.model_id, checkpoint_id)] = adapter_type

    def create(self, model_id, checkpoint_id=None, **kwargs):
        adapter_type = self._adapters.get((model_id, checkpoint_id)) or self._adapters.get(
            (model_id, None)
        )
        if adapter_type:
            return adapter_type(**kwargs)
        phase, status = "unknown", "not_started"
        if self.registry_root:
            models, _ = load_registry(self.registry_root)
            record = next((model for model in models if model.model_id == model_id), None)
            if record:
                phase = record.runtime_phase
                status = record.implementation.adapter_status
        raise AdapterNotImplementedError(
            f"No implemented adapter for model_id={model_id}, checkpoint_id={checkpoint_id}; "
            f"adapter_status={status}; "
            f"runtime_phase={phase}. Implement and smoke-test the adapter before registering it."
        )


def load_adapter(model_id, checkpoint_id, **kwargs):
    """Create a supported adapter without importing its internal module."""

    from .adapters.retfound_cfp import RETFoundCFPAdapter
    from .adapters.retfound_green import RETFoundGreenAdapter
    from .adapters.eyeclip import EyeCLIPAdapter

    factory = AdapterFactory()
    factory.register(RETFoundCFPAdapter)
    factory.register(RETFoundGreenAdapter)
    factory.register(EyeCLIPAdapter)
    return factory.create(model_id, checkpoint_id=checkpoint_id, **kwargs)
