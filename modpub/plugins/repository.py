from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Literal
from ..core.model import Design

class RepositoryPlugin(ABC):
    """Abstract interface for source/destination plugins."""
    name: str

    @abstractmethod
    def read(self, locator: str) -> Design:
        """Read a design from this plugin.
        locator is plugin-specific (e.g., thing id or local path).
        """

    @abstractmethod
    def write(self, design: Design, locator: str, *, mode: Literal["create", "update"]) -> str:
        """Write the design to this plugin; return identifier/path after write."""
