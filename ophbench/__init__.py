"""Stable public consumer API for the ophthalmic model registry."""

from .api import RegistrySnapshot, get_registry_info, list_checkpoints, list_models, load_registry
from .models import load_adapter

__version__ = "0.2.0"

__all__ = [
    "RegistrySnapshot",
    "__version__",
    "get_registry_info",
    "list_checkpoints",
    "list_models",
    "load_adapter",
    "load_registry",
]
