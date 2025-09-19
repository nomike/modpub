"""
Comprehensive tests for LocalDir plugin license handling.

Tests that all license types work correctly with LocalDir serialization,
including round-trip operations and integration with other plugins.
"""
import pytest
from pathlib import Path
from modpub.plugins.localdir.plugin import LocalDirPlugin
from modpub.core.model import Design, License, FileAsset, ImageAsset, Author
from modpub.core.licenses import normalize_license


class TestLocalDirLicenseHandling:
    """Test LocalDir plugin license serialization and round-trip operations."""

    def test_all_thingiverse_licenses_localdir_roundtrip(self, tmp_path: Path):
        """Test that all Thingiverse-supported licenses work with LocalDir round-trip."""
        plugin = LocalDirPlugin()

        # All licenses supported by Thingiverse (from the dropdown list)
        licenses_to_test = [
            License(key="CC0-1.0", name="CC0 1.0 Universal", url="https://creativecommons.org/publicdomain/zero/1.0/"),
            License(key="CC-BY-4.0", name="Creative Commons Attribution 4.0", url="https://creativecommons.org/licenses/by/4.0/"),
            License(key="CC-BY-SA-4.0", name="Creative Commons Attribution-ShareAlike 4.0", url="https://creativecommons.org/licenses/by-sa/4.0/"),
            License(key="CC-BY-NC-4.0", name="Creative Commons Attribution-NonCommercial 4.0", url="https://creativecommons.org/licenses/by-nc/4.0/"),
            License(key="CC-BY-ND-4.0", name="Creative Commons Attribution-NoDerivatives 4.0", url="https://creativecommons.org/licenses/by-nd/4.0/"),
            License(key="CC-BY-NC-SA-4.0", name="Creative Commons Attribution-NonCommercial-ShareAlike 4.0", url="https://creativecommons.org/licenses/by-nc-sa/4.0/"),
            License(key="CC-BY-NC-ND-4.0", name="Creative Commons Attribution-NonCommercial-NoDerivatives 4.0", url="https://creativecommons.org/licenses/by-nc-nd/4.0/"),
            License(key="GPL-3.0", name="GNU General Public License v3.0", url="https://www.gnu.org/licenses/gpl-3.0.en.html"),
            License(key="LGPL-2.1", name="GNU Lesser General Public License v2.1", url="https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html"),
            License(key="BSD", name="BSD License", url="https://opensource.org/licenses/BSD-3-Clause"),
        ]

        for license_obj in licenses_to_test:
            # Create a design with this license
            design = Design(
                title=f"Test Design - {license_obj.key}",
                description_md=f"Test design with {license_obj.key} license",
                instructions_md="Print with standard settings",
                license=license_obj,
                author=Author(name="Test Author"),
                files=[],
                images=[],
            )

            # Write to LocalDir
            test_dir = tmp_path / f"test_{license_obj.key.replace('-', '_').replace('.', '_')}"
            plugin.write(design, str(test_dir), mode="create")

            # Verify directory structure was created
            assert test_dir.exists()
            assert (test_dir / "metadata.json").exists()
            assert (test_dir / "README.md").exists()

            # Read back from LocalDir
            restored_design = plugin.read(str(test_dir))

            # Verify license was preserved correctly
            assert restored_design.license is not None, f"License was lost for {license_obj.key}"
            assert restored_design.license.key == license_obj.key, f"License key mismatch for {license_obj.key}"
            assert restored_design.license.name == license_obj.name, f"License name mismatch for {license_obj.key}"
            assert restored_design.license.url == license_obj.url, f"License URL mismatch for {license_obj.key}"

            # Verify other fields preserved
            assert restored_design.title == design.title
            assert restored_design.description_md == design.description_md
            assert restored_design.instructions_md == design.instructions_md

    def test_license_json_serialization(self, tmp_path: Path):
        """Test that license objects serialize correctly to JSON in metadata.json."""
        plugin = LocalDirPlugin()

        # Test a specific license with all fields
        license_obj = License(
            key="CC-BY-SA-4.0",
            name="Creative Commons Attribution-ShareAlike 4.0",
            url="https://creativecommons.org/licenses/by-sa/4.0/"
        )

        design = Design(
            title="JSON Serialization Test",
            license=license_obj,
            files=[],
            images=[],
        )

        # Write to LocalDir
        test_dir = tmp_path / "json_test"
        plugin.write(design, str(test_dir), mode="create")

        # Check the actual JSON content
        metadata_file = test_dir / "metadata.json"
        json_content = metadata_file.read_text(encoding="utf-8")

        # Verify license fields are present in JSON
        assert '"key": "CC-BY-SA-4.0"' in json_content
        assert '"name": "Creative Commons Attribution-ShareAlike 4.0"' in json_content
        assert '"url": "https://creativecommons.org/licenses/by-sa/4.0/"' in json_content

    def test_none_license_handling(self, tmp_path: Path):
        """Test that designs with no license (None) work correctly."""
        plugin = LocalDirPlugin()

        design = Design(
            title="No License Test",
            description_md="Design with no license",
            license=None,  # Explicitly no license
            files=[],
            images=[],
        )

        # Write and read back
        test_dir = tmp_path / "no_license_test"
        plugin.write(design, str(test_dir), mode="create")
        restored_design = plugin.read(str(test_dir))

        # Verify no license is preserved
        assert restored_design.license is None
        assert restored_design.title == design.title

    def test_license_normalization_integration(self, tmp_path: Path):
        """Test that license normalization works correctly with LocalDir."""
        plugin = LocalDirPlugin()

        # Test various input formats that should normalize to the same license
        test_cases = [
            ("cc-by", "CC-BY-4.0"),
            ("creative commons - attribution", "CC-BY-4.0"),
            ("gpl3", "GPL-3.0"),
            ("bsd license", "BSD"),
        ]

        for input_license, expected_canonical in test_cases:
            # Normalize the license
            normalized = normalize_license(input_license)

            design = Design(
                title=f"Normalization Test - {input_license}",
                license=normalized,
                files=[],
                images=[],
            )

            # Write and read back
            test_dir = tmp_path / f"norm_test_{input_license.replace(' ', '_').replace('-', '_')}"
            plugin.write(design, str(test_dir), mode="create")
            restored_design = plugin.read(str(test_dir))

            # Verify normalized license was preserved
            assert restored_design.license is not None
            assert restored_design.license.key == expected_canonical

    def test_localdir_to_thingiverse_license_workflow(self, tmp_path: Path):
        """Test the complete workflow: LocalDir → canonical → Thingiverse mapping."""
        from modpub.plugins.thingiverse.plugin import ThingiversePlugin
        from modpub.core.licenses import map_for_platform

        # Register Thingiverse license mappings
        ThingiversePlugin.register_license_mappings()

        localdir_plugin = LocalDirPlugin()

        # Test cases: (canonical_license_key, expected_thingiverse_id)
        test_cases = [
            ("CC0-1.0", "cc-zero"),
            ("CC-BY-4.0", "cc"),
            ("CC-BY-SA-4.0", "cc-sa"),
            ("CC-BY-NC-4.0", "cc-nc"),
            ("CC-BY-ND-4.0", "cc-nd"),
            ("CC-BY-NC-SA-4.0", "cc-nc-sa"),
            ("CC-BY-NC-ND-4.0", "cc-nc-nd"),
            ("GPL-3.0", "gpl"),
            ("LGPL-2.1", "lgpl"),
            ("BSD", "bsd"),
        ]

        for canonical_key, expected_thingiverse_id in test_cases:
            # Create design with canonical license
            license_obj = normalize_license(canonical_key)
            design = Design(
                title=f"Workflow Test - {canonical_key}",
                license=license_obj,
                files=[],
                images=[],
            )

            # 1. Write to LocalDir
            test_dir = tmp_path / f"workflow_{canonical_key.replace('-', '_').replace('.', '_')}"
            localdir_plugin.write(design, str(test_dir), mode="create")

            # 2. Read back from LocalDir
            restored_design = localdir_plugin.read(str(test_dir))

            # 3. Verify license survived LocalDir round-trip
            assert restored_design.license is not None
            assert restored_design.license.key == canonical_key

            # 4. Verify it can be mapped to Thingiverse
            thingiverse_id = map_for_platform(restored_design.license, "thingiverse")
            assert thingiverse_id == expected_thingiverse_id, \
                f"Failed Thingiverse mapping for {canonical_key}: expected {expected_thingiverse_id}, got {thingiverse_id}"

    def test_license_with_files_and_images(self, tmp_path: Path):
        """Test license handling with actual files and images."""
        plugin = LocalDirPlugin()

        # Create test files
        src_file = tmp_path / "test.stl"
        src_file.write_bytes(b"test file content")
        src_image = tmp_path / "test.jpg"
        src_image.write_bytes(b"test image content")

        # Create design with license and assets
        license_obj = License(
            key="CC-BY-NC-SA-4.0",
            name="Creative Commons Attribution-NonCommercial-ShareAlike 4.0",
            url="https://creativecommons.org/licenses/by-nc-sa/4.0/"
        )

        design = Design(
            title="License with Assets Test",
            description_md="Test design with license, files, and images",
            license=license_obj,
            author=Author(name="Test Author"),
            files=[FileAsset(filename="test.stl", path=str(src_file))],
            images=[ImageAsset(filename="test.jpg", path=str(src_image))],
        )

        # Write to LocalDir
        test_dir = tmp_path / "assets_test"
        plugin.write(design, str(test_dir), mode="create")

        # Verify structure
        assert (test_dir / "metadata.json").exists()
        assert (test_dir / "README.md").exists()
        assert (test_dir / "files" / "test.stl").exists()
        assert (test_dir / "images" / "test.jpg").exists()

        # Read back
        restored_design = plugin.read(str(test_dir))

        # Verify everything was preserved
        assert restored_design.license is not None
        assert restored_design.license.key == "CC-BY-NC-SA-4.0"
        assert restored_design.license.name == license_obj.name
        assert restored_design.license.url == license_obj.url
        assert len(restored_design.files) == 1
        assert len(restored_design.images) == 1
        assert restored_design.files[0].filename == "test.stl"
        assert restored_design.images[0].filename == "test.jpg"

    def test_update_mode_preserves_license(self, tmp_path: Path):
        """Test that update mode correctly preserves and updates license information."""
        plugin = LocalDirPlugin()

        # Initial design with one license
        original_license = License(key="CC-BY-4.0", name="Creative Commons Attribution 4.0")
        design1 = Design(
            title="Update Test",
            license=original_license,
            files=[],
            images=[],
        )

        test_dir = tmp_path / "update_test"

        # Write initial version
        plugin.write(design1, str(test_dir), mode="create")

        # Update with different license
        updated_license = License(key="CC-BY-SA-4.0", name="Creative Commons Attribution-ShareAlike 4.0")
        design2 = Design(
            title="Update Test - Modified",
            license=updated_license,
            files=[],
            images=[],
        )

        # Write update
        plugin.write(design2, str(test_dir), mode="update")

        # Read back and verify update worked
        final_design = plugin.read(str(test_dir))
        assert final_design.license is not None
        assert final_design.license.key == "CC-BY-SA-4.0"
        assert final_design.title == "Update Test - Modified"


class TestLocalDirLicenseEdgeCases:
    """Test edge cases and error conditions for LocalDir license handling."""

    def test_malformed_license_json_handling(self, tmp_path: Path):
        """Test handling of malformed license data in metadata.json."""
        # Create a metadata.json with malformed license data
        test_dir = tmp_path / "malformed_test"
        test_dir.mkdir()

        # Write malformed JSON (license as string instead of object)
        malformed_json = '''
        {
            "title": "Malformed License Test",
            "description_md": "",
            "instructions_md": "",
            "tags": [],
            "categories": [],
            "license": "not-an-object",
            "author": null,
            "files": [],
            "images": [],
            "derivatives": [],
            "platform": null,
            "platform_id": null,
            "public_url": null,
            "extra": {}
        }
        '''

        (test_dir / "metadata.json").write_text(malformed_json)

        plugin = LocalDirPlugin()

        # This should raise an error when trying to read malformed license data
        with pytest.raises(Exception):  # Could be TypeError, ValidationError, etc.
            plugin.read(str(test_dir))

    def test_license_with_special_characters(self, tmp_path: Path):
        """Test license handling with special characters in names and URLs."""
        plugin = LocalDirPlugin()

        # License with special characters
        license_obj = License(
            key="CUSTOM-1.0",
            name="Custom License™ with Special Characters & Symbols",
            url="https://example.com/license?version=1.0&type=custom"
        )

        design = Design(
            title="Special Characters Test",
            license=license_obj,
            files=[],
            images=[],
        )

        test_dir = tmp_path / "special_chars_test"
        plugin.write(design, str(test_dir), mode="create")
        restored_design = plugin.read(str(test_dir))

        assert restored_design.license is not None
        assert restored_design.license.key == "CUSTOM-1.0"
        assert restored_design.license.name == "Custom License™ with Special Characters & Symbols"
        assert restored_design.license.url == "https://example.com/license?version=1.0&type=custom"