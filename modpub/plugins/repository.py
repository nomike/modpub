from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Literal
from ..core.model import Design

class RepositoryPlugin(ABC):
    """Abstract interface for source/destination plugins."""
    name: str

    @classmethod
    def register_license_mappings(cls) -> None:
        """Register platform-specific license mappings.

        Override this method to register license mappings for your platform.
        Use register_platform_license_mapping() to map canonical license keys
        to platform-specific identifiers.

        Example:
            register_platform_license_mapping("myplatform", "CC-BY-4.0", "attribution")
            register_platform_license_mapping("myplatform", "GPL-3.0", "gpl3")
        """
        pass

    @abstractmethod
    def read(self, locator: str) -> Design:
        """Read a design from this plugin.
        locator is plugin-specific (e.g., thing id or local path).
        """

    @abstractmethod
    def write(self, design: Design, locator: str, *, mode: Literal["create", "update"]) -> str:
        """Write the design to this plugin; return identifier/path after write."""
