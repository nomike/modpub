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
    # GPL
    "gpl-3.0": License(key="GPL-3.0", name="GNU General Public License v3.0", url="https://www.gnu.org/licenses/gpl-3.0.en.html"),
    "gpl3": License(key="GPL-3.0", name="GNU General Public License v3.0", url="https://www.gnu.org/licenses/gpl-3.0.en.html"),
    # BSD licenses
    "bsd license": License(key="BSD", name="BSD License", url="https://opensource.org/licenses/BSD-3-Clause"),
    "bsd": License(key="BSD", name="BSD License", url="https://opensource.org/licenses/BSD-3-Clause"),
}

_THINGIVERSE_OUTBOUND = {
    "CC0-1.0": "cc-zero",
    "CC-BY-4.0": "cc",
    "CC-BY-SA-4.0": "cc-sa",
    "CC-BY-NC-4.0": "cc-nc",
    "GPL-3.0": "gpl",
    "BSD": "bsd",
}

_PRINTABLES_OUTBOUND = {
    "CC0-1.0": "cc0",
    "CC-BY-4.0": "cc-by",
    "CC-BY-SA-4.0": "cc-by-sa",
    "CC-BY-NC-4.0": "cc-by-nc",
    "GPL-3.0": "gpl-3.0",
}


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
    if not license_obj:
        return None
    key = license_obj.key
    if platform == "thingiverse":
        return _THINGIVERSE_OUTBOUND.get(key)
    if platform == "printables":
        return _PRINTABLES_OUTBOUND.get(key)
    return None
