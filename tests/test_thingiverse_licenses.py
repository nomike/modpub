"""
Comprehensive tests for Thingiverse license mappings.

Tests all known Thingiverse license values and verifies bidirectional mapping.
"""
import pytest
from modpub.core.model import License
from modpub.core.licenses import (
    map_for_platform,
    map_from_platform,
    normalize_license,
)


@pytest.fixture(autouse=True)
def setup_thingiverse_licenses():
    """Initialize Thingiverse plugin to register license mappings."""
    from modpub.plugins.thingiverse.plugin import ThingiversePlugin
    ThingiversePlugin.register_license_mappings()


class TestThingiverseLicenseMappings:
    """Test suite for Thingiverse license mappings."""

    def test_cc_zero_mapping(self):
        """Test CC0 (Public Domain) license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="CC0-1.0")
        assert map_for_platform(license_obj, "thingiverse") == "cc-zero"

        # Thingiverse to canonical
        assert map_from_platform("cc-zero", "thingiverse") == "CC0-1.0"

        # Round trip test
        canonical_key = map_from_platform("cc-zero", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "cc-zero"

    def test_cc_by_mapping(self):
        """Test CC-BY (Attribution) license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="CC-BY-4.0")
        assert map_for_platform(license_obj, "thingiverse") == "cc"

        # Thingiverse to canonical
        assert map_from_platform("cc", "thingiverse") == "CC-BY-4.0"

        # Test case variations
        assert map_from_platform("CC", "thingiverse") == "CC-BY-4.0"
        assert map_from_platform(" cc ", "thingiverse") == "CC-BY-4.0"

        # Round trip test
        canonical_key = map_from_platform("cc", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "cc"

    def test_cc_by_sa_mapping(self):
        """Test CC-BY-SA (Attribution-ShareAlike) license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="CC-BY-SA-4.0")
        assert map_for_platform(license_obj, "thingiverse") == "cc-sa"

        # Thingiverse to canonical
        assert map_from_platform("cc-sa", "thingiverse") == "CC-BY-SA-4.0"

        # Round trip test
        canonical_key = map_from_platform("cc-sa", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "cc-sa"

    def test_cc_by_nc_mapping(self):
        """Test CC-BY-NC (Attribution-NonCommercial) license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="CC-BY-NC-4.0")
        assert map_for_platform(license_obj, "thingiverse") == "cc-nc"

        # Thingiverse to canonical
        assert map_from_platform("cc-nc", "thingiverse") == "CC-BY-NC-4.0"

        # Round trip test
        canonical_key = map_from_platform("cc-nc", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "cc-nc"

    def test_gpl_mapping(self):
        """Test GPL license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="GPL-3.0")
        assert map_for_platform(license_obj, "thingiverse") == "gpl"

        # Thingiverse to canonical
        assert map_from_platform("gpl", "thingiverse") == "GPL-3.0"

        # Round trip test
        canonical_key = map_from_platform("gpl", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "gpl"

    def test_bsd_mapping(self):
        """Test BSD license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="BSD")
        assert map_for_platform(license_obj, "thingiverse") == "bsd"

        # Thingiverse to canonical
        assert map_from_platform("bsd", "thingiverse") == "BSD"

        # Round trip test
        canonical_key = map_from_platform("bsd", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "bsd"

    def test_cc_by_nd_mapping(self):
        """Test CC-BY-ND (Attribution-NoDerivatives) license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="CC-BY-ND-4.0")
        assert map_for_platform(license_obj, "thingiverse") == "cc-nd"

        # Thingiverse to canonical
        assert map_from_platform("cc-nd", "thingiverse") == "CC-BY-ND-4.0"

        # Round trip test
        canonical_key = map_from_platform("cc-nd", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "cc-nd"

    def test_cc_by_nc_sa_mapping(self):
        """Test CC-BY-NC-SA (Attribution-NonCommercial-ShareAlike) license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="CC-BY-NC-SA-4.0")
        assert map_for_platform(license_obj, "thingiverse") == "cc-nc-sa"

        # Thingiverse to canonical
        assert map_from_platform("cc-nc-sa", "thingiverse") == "CC-BY-NC-SA-4.0"

        # Round trip test
        canonical_key = map_from_platform("cc-nc-sa", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "cc-nc-sa"

    def test_cc_by_nc_nd_mapping(self):
        """Test CC-BY-NC-ND (Attribution-NonCommercial-NoDerivatives) license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="CC-BY-NC-ND-4.0")
        assert map_for_platform(license_obj, "thingiverse") == "cc-nc-nd"

        # Thingiverse to canonical
        assert map_from_platform("cc-nc-nd", "thingiverse") == "CC-BY-NC-ND-4.0"

        # Round trip test
        canonical_key = map_from_platform("cc-nc-nd", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "cc-nc-nd"

    def test_lgpl_mapping(self):
        """Test LGPL license mapping."""
        # Canonical to Thingiverse
        license_obj = License(key="LGPL-2.1")
        assert map_for_platform(license_obj, "thingiverse") == "lgpl"

        # Thingiverse to canonical
        assert map_from_platform("lgpl", "thingiverse") == "LGPL-2.1"

        # Round trip test
        canonical_key = map_from_platform("lgpl", "thingiverse")
        thingiverse_id = map_for_platform(License(key=canonical_key), "thingiverse")
        assert thingiverse_id == "lgpl"

    def test_thingiverse_verbose_license_names(self):
        """Test Thingiverse's verbose license name variations."""
        # Test all verbose license names that Thingiverse returns in the dropdown
        verbose_mappings = {
            "creative commons - public domain dedication": "CC0-1.0",
            "creative commons - attribution": "CC-BY-4.0",
            "creative commons - attribution - share alike": "CC-BY-SA-4.0",
            "creative commons - attribution - no derivatives": "CC-BY-ND-4.0",
            "creative commons - attribution - non-commercial": "CC-BY-NC-4.0",
            "creative commons - attribution - non-commercial - share alike": "CC-BY-NC-SA-4.0",
            "creative commons - attribution - non-commercial - no derivatives": "CC-BY-NC-ND-4.0",
            "gnu - gpl": "GPL-3.0",
            "gnu - lgpl": "LGPL-2.1",
            "bsd license": "BSD",
        }

        for verbose_name, canonical in verbose_mappings.items():
            assert map_from_platform(verbose_name, "thingiverse") == canonical, \
                f"Failed mapping for verbose license: {verbose_name}"

        # Test case insensitive matching
        assert map_from_platform("Creative Commons - Attribution", "thingiverse") == "CC-BY-4.0"
        assert map_from_platform("CREATIVE COMMONS - ATTRIBUTION", "thingiverse") == "CC-BY-4.0"
        assert map_from_platform("GNU - GPL", "thingiverse") == "GPL-3.0"
        assert map_from_platform("BSD License", "thingiverse") == "BSD"

    def test_all_supported_thingiverse_licenses(self):
        """Test that all currently supported licenses are covered."""
        expected_mappings = {
            "CC0-1.0": "cc-zero",
            "CC-BY-4.0": "cc",
            "CC-BY-SA-4.0": "cc-sa",
            "CC-BY-NC-4.0": "cc-nc",
            "CC-BY-ND-4.0": "cc-nd",
            "CC-BY-NC-SA-4.0": "cc-nc-sa",
            "CC-BY-NC-ND-4.0": "cc-nc-nd",
            "GPL-3.0": "gpl",
            "LGPL-2.1": "lgpl",
            "BSD": "bsd",
        }

        for canonical, thingiverse_id in expected_mappings.items():
            # Test outbound mapping
            license_obj = License(key=canonical)
            assert map_for_platform(license_obj, "thingiverse") == thingiverse_id, \
                f"Failed outbound mapping for {canonical}"

            # Test inbound mapping
            assert map_from_platform(thingiverse_id, "thingiverse") == canonical, \
                f"Failed inbound mapping for {thingiverse_id}"

    def test_unknown_thingiverse_license(self):
        """Test handling of unknown Thingiverse license values."""
        # Should return None for unknown licenses
        assert map_from_platform("unknown-license", "thingiverse") is None
        assert map_from_platform("proprietary", "thingiverse") is None
        assert map_from_platform("", "thingiverse") is None

    def test_unsupported_canonical_license(self):
        """Test handling of canonical licenses not supported by Thingiverse."""
        # These licenses don't have Thingiverse mappings
        unsupported_licenses = [
            "MIT",
            "Apache-2.0",
            "MPL-2.0",
            "ISC",
            "Unlicense",
        ]

        for canonical_key in unsupported_licenses:
            license_obj = License(key=canonical_key)
            assert map_for_platform(license_obj, "thingiverse") is None, \
                f"Unexpected mapping found for unsupported license {canonical_key}"

    def test_thingiverse_default_fallback(self):
        """Test that the plugin uses 'cc' as default for unmapped licenses."""
        # This tests the fallback behavior mentioned in the plugin code
        # The plugin should log a warning and use "cc" as default
        # We can't easily test the logging here, but we can verify the behavior
        # by checking that the write() method would use "cc" for unknown licenses
        pass  # This would require more complex integration testing

    def test_license_normalization_workflow(self):
        """Test complete workflow: input → normalize → map to Thingiverse."""
        test_cases = [
            # (input, expected_canonical, expected_thingiverse)
            ("Creative Commons - Attribution", "CC-BY-4.0", "cc"),
            ("cc-by", "CC-BY-4.0", "cc"),
            ("cc0", "CC0-1.0", "cc-zero"),
            ("gpl3", "GPL-3.0", "gpl"),
            ("bsd license", "BSD", "bsd"),
        ]

        for input_license, expected_canonical, expected_thingiverse in test_cases:
            # Normalize input to canonical
            normalized = normalize_license(input_license)
            assert normalized.key == expected_canonical, \
                f"Normalization failed for {input_license}"

            # Map canonical to Thingiverse
            thingiverse_id = map_for_platform(normalized, "thingiverse")
            assert thingiverse_id == expected_thingiverse, \
                f"Thingiverse mapping failed for {expected_canonical}"

    def test_potential_missing_licenses(self):
        """Test for licenses that might be missing from current mappings."""
        # These are licenses commonly used in 3D printing that might be on Thingiverse
        potentially_missing = [
            "Public Domain",     # Alternative to CC0
            "All Rights Reserved", # Proprietary
            "MIT",              # Common open source license
            "Apache-2.0",       # Common open source license
        ]

        # For now, these should return None since they're not mapped
        # If any of these return a value, it means we need to investigate
        for license_name in potentially_missing:
            license_obj = License(key=license_name)
            result = map_for_platform(license_obj, "thingiverse")
            if result is not None:
                pytest.fail(f"Unexpected mapping found for {license_name}: {result}. "
                           f"Consider adding proper support or verify this is correct.")


class TestThingiverseLicenseEdgeCases:
    """Test edge cases and error conditions for Thingiverse license mappings."""

    def test_none_license_handling(self):
        """Test handling of None license values."""
        assert map_for_platform(None, "thingiverse") is None
        assert map_from_platform(None, "thingiverse") is None

    def test_empty_license_handling(self):
        """Test handling of empty license values."""
        empty_license = License(key="", name="")
        assert map_for_platform(empty_license, "thingiverse") is None
        assert map_from_platform("", "thingiverse") is None

    def test_whitespace_handling(self):
        """Test handling of licenses with whitespace."""
        # Leading/trailing whitespace should be handled
        assert map_from_platform("  cc  ", "thingiverse") == "CC-BY-4.0"
        assert map_from_platform("\tcc-zero\n", "thingiverse") == "CC0-1.0"

    def test_case_sensitivity(self):
        """Test case sensitivity in license mapping."""
        # All mappings should be case insensitive
        test_cases = [
            ("cc", "CC-BY-4.0"),
            ("CC", "CC-BY-4.0"),
            ("Cc", "CC-BY-4.0"),
            ("cc-zero", "CC0-1.0"),
            ("CC-ZERO", "CC0-1.0"),
            ("GPL", "GPL-3.0"),
            ("gpl", "GPL-3.0"),
            ("BSD", "BSD"),
            ("bsd", "BSD"),
        ]

        for thingiverse_id, expected_canonical in test_cases:
            assert map_from_platform(thingiverse_id, "thingiverse") == expected_canonical, \
                f"Case sensitivity test failed for {thingiverse_id}"