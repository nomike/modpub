from __future__ import annotations
from importlib.metadata import entry_points
from ..exceptions import ValidationError

_REGISTRY = {}

def register(name: str, cls):
    _REGISTRY[name] = cls

def load_plugin(name: str):
    # Try entry points first
    eps = entry_points(group="modpub.plugins")
    for ep in eps:
        if ep.name == name:
            plugin_class = ep.load()
            return plugin_class()

    # Fallback registry
    if name in _REGISTRY:
        return _REGISTRY[name]()

    raise ValidationError(f"Unknown plugin: {name}")
