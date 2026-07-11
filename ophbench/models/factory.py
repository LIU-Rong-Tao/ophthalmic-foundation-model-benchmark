from pathlib import Path

from ophbench.registry.loader import load_registry

from .errors import AdapterNotImplementedError


class AdapterFactory:
    def __init__(self, registry_root=None):
        self._adapters = {}
        self.registry_root = Path(registry_root) if registry_root else None

    def register(self, adapter_type):
        self._adapters[adapter_type.model_id] = adapter_type

    def create(self, model_id, **kwargs):
        if model_id in self._adapters:
            return self._adapters[model_id](**kwargs)
        phase, status = "unknown", "not_started"
        if self.registry_root:
            models, _ = load_registry(self.registry_root)
            record = next((model for model in models if model.model_id == model_id), None)
            if record:
                phase = record.runtime_phase
                status = record.implementation.adapter_status
        raise AdapterNotImplementedError(
            f"No implemented adapter for model_id={model_id}; adapter_status={status}; "
            f"runtime_phase={phase}. Implement and smoke-test the adapter before registering it."
        )
