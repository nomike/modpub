from __future__ import annotations
from typing import Optional, Dict
from .model import License

# Canonical license map (SPDX-like for CC)
_CANONICAL: Dict[str, License] = {
    # CC0
    "cc0": License(key="CC0-1.0", name="CC0 1.0 Universal", url="https://creativecommons.org/publicdomain/zero/1.0/"),
    "cc0-1.0": License(key="CC0-1.0", name="CC0 1.0 Universal", url="https://creativecommons.org/publicdomain/zero/1.0/"),
    # CC-BY
    "cc-by": License(key="CC-BY-4.0", name="Creative Commons Attribution 4.0", url="https://creativecommons.org/licenses/by/4.0/"),
    "cc-by-4.0": License(key="CC-BY-4.0", name="Creative Commons Attribution 4.0", url="https://creativecommons.org/licenses/by/4.0/"),
    "creative commons - attribution": License(key="CC-BY-4.0", name="Creative Commons Attribution 4.0", url="https://creativecommons.org/licenses/by/4.0/"),
    # CC-BY-SA
    "cc-by-sa": License(key="CC-BY-SA-4.0", name="Creative Commons Attribution-ShareAlike 4.0", url="https://creativecommons.org/licenses/by-sa/4.0/"),
    "cc-by-sa-4.0": License(key="CC-BY-SA-4.0", name="Creative Commons Attribution-ShareAlike 4.0", url="https://creativecommons.org/licenses/by-sa/4.0/"),
    "creative commons - attribution - share alike": License(key="CC-BY-SA-4.0", name="Creative Commons Attribution-ShareAlike 4.0", url="https://creativecommons.org/licenses/by-sa/4.0/"),
    # CC-BY-NC
    "cc-by-nc": License(key="CC-BY-NC-4.0", name="Creative Commons Attribution-NonCommercial 4.0", url="https://creativecommons.org/licenses/by-nc/4.0/"),
    "cc-by-nc-4.0": License(key="CC-BY-NC-4.0", name="Creative Commons Attribution-NonCommercial 4.0", url="https://creativecommons.org/licenses/by-nc/4.0/"),
    # CC-BY-ND
    "cc-by-nd": License(key="CC-BY-ND-4.0", name="Creative Commons Attribution-NoDerivatives 4.0", url="https://creativecommons.org/licenses/by-nd/4.0/"),
    "cc-by-nd-4.0": License(key="CC-BY-ND-4.0", name="Creative Commons Attribution-NoDerivatives 4.0", url="https://creativecommons.org/licenses/by-nd/4.0/"),
    # CC-BY-NC-SA
    "cc-by-nc-sa": License(key="CC-BY-NC-SA-4.0", name="Creative Commons Attribution-NonCommercial-ShareAlike 4.0", url="https://creativecommons.org/licenses/by-nc-sa/4.0/"),
    "cc-by-nc-sa-4.0": License(key="CC-BY-NC-SA-4.0", name="Creative Commons Attribution-NonCommercial-ShareAlike 4.0", url="https://creativecommons.org/licenses/by-nc-sa/4.0/"),
    # CC-BY-NC-ND
    "cc-by-nc-nd": License(key="CC-BY-NC-ND-4.0", name="Creative Commons Attribution-NonCommercial-NoDerivatives 4.0", url="https://creativecommons.org/licenses/by-nc-nd/4.0/"),
    "cc-by-nc-nd-4.0": License(key="CC-BY-NC-ND-4.0", name="Creative Commons Attribution-NonCommercial-NoDerivatives 4.0", url="https://creativecommons.org/licenses/by-nc-nd/4.0/"),
    # GPL
    "gpl-3.0": License(key="GPL-3.0", name="GNU General Public License v3.0", url="https://www.gnu.org/licenses/gpl-3.0.en.html"),
    "gpl3": License(key="GPL-3.0", name="GNU General Public License v3.0", url="https://www.gnu.org/licenses/gpl-3.0.en.html"),
    # LGPL
    "lgpl-2.1": License(key="LGPL-2.1", name="GNU Lesser General Public License v2.1", url="https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html"),
    "lgpl": License(key="LGPL-2.1", name="GNU Lesser General Public License v2.1", url="https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html"),
    # BSD licenses
    "bsd license": License(key="BSD", name="BSD License", url="https://opensource.org/licenses/BSD-3-Clause"),
    "bsd": License(key="BSD", name="BSD License", url="https://opensource.org/licenses/BSD-3-Clause"),
}

# Platform-specific license mappings (canonical -> platform-specific)
# These are populated by plugins via register_platform_license_mapping()
_PLATFORM_OUTBOUND: Dict[str, Dict[str, str]] = {}

# Platform-specific license mappings (platform-specific -> canonical)
# These are populated by plugins via register_platform_license_mapping()
_PLATFORM_INBOUND: Dict[str, Dict[str, str]] = {}


def normalize_license_name(name: Optional[str]) -> Optional[License]:
    if not name:
        return None
    key = name.strip().lower()
    return _CANONICAL.get(key)


def normalize_license(lic: Optional[License | str]) -> Optional[License]:
    if lic is None:
        return None
    if isinstance(lic, str):
        res = normalize_license_name(lic)
        return res or License(key=lic, name=lic)
    res = normalize_license_name(lic.key) or normalize_license_name(lic.name)
    return res or lic


def map_for_platform(license_obj: Optional[License], platform: str) -> Optional[str]:
    """Map a canonical license to platform-specific identifier."""
    if not license_obj:
        return None
    key = license_obj.key
    return _PLATFORM_OUTBOUND.get(platform, {}).get(key)


def map_from_platform(platform_license: Optional[str], platform: str) -> Optional[str]:
    """Map a platform-specific license identifier to canonical license key."""
    if not platform_license:
        return None
    return _PLATFORM_INBOUND.get(platform, {}).get(platform_license.strip().lower())


def register_platform_license_mapping(platform: str, canonical_key: str, platform_id: str) -> None:
    """Register a new license mapping for a platform. Useful for plugin extensibility."""
    if platform not in _PLATFORM_OUTBOUND:
        _PLATFORM_OUTBOUND[platform] = {}
    if platform not in _PLATFORM_INBOUND:
        _PLATFORM_INBOUND[platform] = {}

    _PLATFORM_OUTBOUND[platform][canonical_key] = platform_id
    _PLATFORM_INBOUND[platform][platform_id.lower()] = canonical_key


def register_platform_inbound_mapping(platform: str, platform_id: str, canonical_key: str) -> None:
    """Register a one-way inbound mapping (platform -> canonical). Useful for platform variations."""
    if platform not in _PLATFORM_INBOUND:
        _PLATFORM_INBOUND[platform] = {}
    _PLATFORM_INBOUND[platform][platform_id.lower()] = canonical_key


def register_canonical_license(input_name: str, license_obj: License) -> None:
    """Register a new canonical license mapping. Useful for plugin extensibility."""
    _CANONICAL[input_name.strip().lower()] = license_obj


def get_supported_platforms() -> list[str]:
    """Get list of platforms with license mapping support."""
    return list(_PLATFORM_OUTBOUND.keys())
