from __future__ import annotations
from importlib.metadata import entry_points
from ..exceptions import ValidationError

_REGISTRY = {}

def register(name: str, cls):
    _REGISTRY[name] = cls

def load_plugin(name: str):
    # Try entry points first
    try:
        eps = entry_points(group="modpub.plugins")
        for ep in eps:
            if ep.name == name:
                return ep.load()()
    except Exception:
        pass
    # Fallback registry
    if name in _REGISTRY:
        return _REGISTRY[name]()
    raise ValidationError(f"Unknown plugin: {name}")
