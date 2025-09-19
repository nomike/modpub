import pytest
from modpub.core.model import License
from modpub.core.licenses import (
    normalize_license,
    normalize_license_name,
    map_for_platform,
    map_from_platform,
    register_platform_license_mapping,
    register_canonical_license,
    get_supported_platforms,
)


@pytest.fixture(autouse=True)
def setup_plugins():
    """Initialize plugins to register their license mappings."""
    # Import plugin classes and register their license mappings
    from modpub.plugins.thingiverse.plugin import ThingiversePlugin

    # Register license mappings without instantiating plugins
    ThingiversePlugin.register_license_mappings()

    # Register test mappings for a mock "printables" platform
    from modpub.core.licenses import register_platform_license_mapping
    register_platform_license_mapping("printables", "CC0-1.0", "cc0")
    register_platform_license_mapping("printables", "CC-BY-4.0", "cc-by")
    register_platform_license_mapping("printables", "CC-BY-SA-4.0", "cc-by-sa")
    register_platform_license_mapping("printables", "CC-BY-NC-4.0", "cc-by-nc")
    register_platform_license_mapping("printables", "GPL-3.0", "gpl-3.0")


def test_normalize_license_name():
    # Test canonical license names
    assert normalize_license_name("CC-BY-4.0").key == "CC-BY-4.0"
    assert normalize_license_name("cc-by-4.0").key == "CC-BY-4.0"
    assert normalize_license_name("cc-by").key == "CC-BY-4.0"

    # Test variations
    assert normalize_license_name("Creative Commons - Attribution").key == "CC-BY-4.0"
    assert normalize_license_name("bsd license").key == "BSD"
    assert normalize_license_name("gpl3").key == "GPL-3.0"

    # Test unknown license
    assert normalize_license_name("unknown-license") is None
    assert normalize_license_name(None) is None
    assert normalize_license_name("") is None


def test_normalize_license():
    # Test License object normalization
    lic = License(key="cc-by", name="Some name")
    normalized = normalize_license(lic)
    assert normalized.key == "CC-BY-4.0"
    assert normalized.name == "Creative Commons Attribution 4.0"

    # Test string normalization
    normalized = normalize_license("cc-by-sa")
    assert normalized.key == "CC-BY-SA-4.0"

    # Test unknown license preservation
    unknown_lic = License(key="custom-license", name="Custom License")
    normalized = normalize_license(unknown_lic)
    assert normalized.key == "custom-license"
    assert normalized.name == "Custom License"

    # Test string unknown license
    normalized = normalize_license("custom-license")
    assert normalized.key == "custom-license"
    assert normalized.name == "custom-license"

    # Test None input
    assert normalize_license(None) is None


def test_map_for_platform():
    # Test Thingiverse mappings
    lic = License(key="CC-BY-4.0")
    assert map_for_platform(lic, "thingiverse") == "cc"

    lic = License(key="CC0-1.0")
    assert map_for_platform(lic, "thingiverse") == "cc-zero"

    lic = License(key="GPL-3.0")
    assert map_for_platform(lic, "thingiverse") == "gpl"

    # Test Printables mappings
    lic = License(key="CC-BY-4.0")
    assert map_for_platform(lic, "printables") == "cc-by"

    lic = License(key="GPL-3.0")
    assert map_for_platform(lic, "printables") == "gpl-3.0"

    # Test unknown platform
    lic = License(key="CC-BY-4.0")
    assert map_for_platform(lic, "unknown-platform") is None

    # Test unknown license
    lic = License(key="unknown-license")
    assert map_for_platform(lic, "thingiverse") is None

    # Test None input
    assert map_for_platform(None, "thingiverse") is None


def test_map_from_platform():
    # Test Thingiverse reverse mappings
    assert map_from_platform("cc", "thingiverse") == "CC-BY-4.0"
    assert map_from_platform("cc-zero", "thingiverse") == "CC0-1.0"
    assert map_from_platform("gpl", "thingiverse") == "GPL-3.0"
    assert map_from_platform("Creative Commons - Attribution", "thingiverse") == "CC-BY-4.0"

    # Test case insensitive
    assert map_from_platform("CC", "thingiverse") == "CC-BY-4.0"
    assert map_from_platform(" cc ", "thingiverse") == "CC-BY-4.0"

    # Test Printables reverse mappings
    assert map_from_platform("cc-by", "printables") == "CC-BY-4.0"
    assert map_from_platform("gpl-3.0", "printables") == "GPL-3.0"

    # Test unknown platform
    assert map_from_platform("cc", "unknown-platform") is None

    # Test unknown license
    assert map_from_platform("unknown-license", "thingiverse") is None

    # Test None input
    assert map_from_platform(None, "thingiverse") is None
    assert map_from_platform("", "thingiverse") is None


def test_register_platform_license_mapping():
    # Register a new platform
    register_platform_license_mapping("newplatform", "CC-BY-4.0", "attribution")

    # Test the mapping works
    lic = License(key="CC-BY-4.0")
    assert map_for_platform(lic, "newplatform") == "attribution"
    assert map_from_platform("attribution", "newplatform") == "CC-BY-4.0"

    # Register additional license for same platform
    register_platform_license_mapping("newplatform", "GPL-3.0", "gpl3")
    lic = License(key="GPL-3.0")
    assert map_for_platform(lic, "newplatform") == "gpl3"
    assert map_from_platform("gpl3", "newplatform") == "GPL-3.0"

    # Original mapping should still work
    lic = License(key="CC-BY-4.0")
    assert map_for_platform(lic, "newplatform") == "attribution"


def test_register_canonical_license():
    # Register a new canonical license
    custom_license = License(key="CUSTOM-1.0", name="Custom License 1.0", url="https://example.com/custom")
    register_canonical_license("custom", custom_license)

    # Test normalization works
    normalized = normalize_license_name("custom")
    assert normalized.key == "CUSTOM-1.0"
    assert normalized.name == "Custom License 1.0"
    assert normalized.url == "https://example.com/custom"

    # Test case insensitive
    register_canonical_license("Another Custom", custom_license)
    normalized = normalize_license_name("ANOTHER CUSTOM")
    assert normalized.key == "CUSTOM-1.0"


def test_get_supported_platforms():
    platforms = get_supported_platforms()
    assert "thingiverse" in platforms
    assert "printables" in platforms
    assert isinstance(platforms, list)


def test_round_trip_license_mapping():
    """Test that licenses can be mapped to platform and back without loss."""
    # Test Thingiverse round trip
    original_license = License(key="CC-BY-4.0")
    platform_id = map_for_platform(original_license, "thingiverse")
    canonical_key = map_from_platform(platform_id, "thingiverse")
    assert canonical_key == "CC-BY-4.0"

    # Test Printables round trip
    platform_id = map_for_platform(original_license, "printables")
    canonical_key = map_from_platform(platform_id, "printables")
    assert canonical_key == "CC-BY-4.0"


def test_full_workflow():
    """Test complete license workflow: input -> normalize -> platform -> reverse."""
    # Start with a common input format
    input_license = "Creative Commons - Attribution"

    # Normalize to canonical
    normalized = normalize_license(input_license)
    assert normalized.key == "CC-BY-4.0"

    # Map to Thingiverse
    thingiverse_id = map_for_platform(normalized, "thingiverse")
    assert thingiverse_id == "cc"

    # Map back from Thingiverse
    canonical_key = map_from_platform(thingiverse_id, "thingiverse")
    assert canonical_key == "CC-BY-4.0"

    # Verify we can recreate the normalized license
    final_license = normalize_license(canonical_key)
    assert final_license.key == normalized.key
    assert final_license.name == normalized.name