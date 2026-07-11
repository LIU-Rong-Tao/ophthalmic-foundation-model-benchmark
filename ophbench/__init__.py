"""Stable public consumer API for the ophthalmic model registry."""

from .api import RegistrySnapshot, get_registry_info, list_checkpoints, list_models, load_registry

__version__ = "0.1.1"

__all__ = [
    "RegistrySnapshot",
    "__version__",
    "get_registry_info",
    "list_checkpoints",
    "list_models",
    "load_registry",
]
