from __future__ import annotations
import logging
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import Literal

import requests

from ...core.model import Design, Author, License, FileAsset, ImageAsset
from ...core.storage import ensure_dir, sha256_file
from ...core.licenses import normalize_license, map_for_platform, map_from_platform, register_platform_license_mapping, register_platform_inbound_mapping
from ...exceptions import ValidationError
from ..repository import RepositoryPlugin
from .api import ThingiverseAPI

LOGGER = logging.getLogger("modpub.thingiverse.plugin")

class ThingiversePlugin(RepositoryPlugin):
    """Thingiverse provider plugin (read/create/update)."""
    name = "thingiverse"

    def __init__(self) -> None:
        self._register_license_mappings()
        self.api = ThingiverseAPI()

    @classmethod
    def register_license_mappings(cls) -> None:
        """Register Thingiverse-specific license mappings."""
        # Register mappings from canonical to Thingiverse format
        register_platform_license_mapping("thingiverse", "CC0-1.0", "cc-zero")
        register_platform_license_mapping("thingiverse", "CC-BY-4.0", "cc")
        register_platform_license_mapping("thingiverse", "CC-BY-SA-4.0", "cc-sa")
        register_platform_license_mapping("thingiverse", "CC-BY-NC-4.0", "cc-nc")
        register_platform_license_mapping("thingiverse", "CC-BY-ND-4.0", "cc-nd")
        register_platform_license_mapping("thingiverse", "CC-BY-NC-SA-4.0", "cc-nc-sa")
        register_platform_license_mapping("thingiverse", "CC-BY-NC-ND-4.0", "cc-nc-nd")
        register_platform_license_mapping("thingiverse", "GPL-3.0", "gpl")
        register_platform_license_mapping("thingiverse", "LGPL-2.1", "lgpl")
        register_platform_license_mapping("thingiverse", "BSD", "bsd")

        # Register additional inbound mappings for verbose license names Thingiverse returns
        register_platform_inbound_mapping("thingiverse", "creative commons - public domain dedication", "CC0-1.0")
        register_platform_inbound_mapping("thingiverse", "creative commons - attribution", "CC-BY-4.0")
        register_platform_inbound_mapping("thingiverse", "creative commons - attribution - share alike", "CC-BY-SA-4.0")
        register_platform_inbound_mapping("thingiverse", "creative commons - attribution - no derivatives", "CC-BY-ND-4.0")
        register_platform_inbound_mapping("thingiverse", "creative commons - attribution - non-commercial", "CC-BY-NC-4.0")
        register_platform_inbound_mapping("thingiverse", "creative commons - attribution - non-commercial - share alike", "CC-BY-NC-SA-4.0")
        register_platform_inbound_mapping("thingiverse", "creative commons - attribution - non-commercial - no derivatives", "CC-BY-NC-ND-4.0")
        register_platform_inbound_mapping("thingiverse", "gnu - gpl", "GPL-3.0")
        register_platform_inbound_mapping("thingiverse", "gnu - lgpl", "LGPL-2.1")
        register_platform_inbound_mapping("thingiverse", "bsd license", "BSD")

    def _register_license_mappings(self) -> None:
        """Register license mappings when plugin is instantiated."""
        self.register_license_mappings()

    def read(self, locator: str) -> Design:
        thing_id = locator.strip()
        data = self.api.get_thing(thing_id)
        files = self.api.get_thing_files(thing_id)
        images = self.api.get_thing_images(thing_id)
        tags = [t.get("name") for t in self.api.get_thing_tags(thing_id)]

        author = Author(
            name=data.get("creator", {}).get("name", ""),
            url=data.get("creator", {}).get("public_url"),
            user_id=str(data.get("creator", {}).get("id")) if data.get("creator", {}).get("id") is not None else None,
        )
        license_obj = None
        lic_name = data.get("license") or data.get("license_name")
        if lic_name:
            # First try to map from Thingiverse-specific license to canonical
            canonical_key = map_from_platform(str(lic_name), "thingiverse")
            if canonical_key:
                license_obj = normalize_license(canonical_key)
            else:
                # Fallback to direct normalization for unknown licenses
                license_obj = normalize_license(License(key=str(lic_name), name=str(lic_name)))

        design = Design(
            title=data.get("name", f"thing:{thing_id}"),
            description_md=data.get("description", ""),
            instructions_md=data.get("instructions", ""),
            tags=[t for t in tags if t],
            categories=[],
            license=license_obj,
            author=author,
            platform="thingiverse",
            platform_id=str(data.get("id")),
            public_url=data.get("public_url"),
            extra={"raw": data},
        )

        tmpdir = Path(tempfile.mkdtemp(prefix=f"modpub_{thing_id}_"))
        files_dir = tmpdir / "files"
        images_dir = tmpdir / "images"
        ensure_dir(files_dir)
        ensure_dir(images_dir)

        sess = self.api.session
        headers = self.api._headers()

        for fmeta in files:
            url = fmeta.get("download_url") or fmeta.get("public_url") or fmeta.get("url")
            if not url:
                continue
            fname = fmeta.get("name") or fmeta.get("filename") or os.path.basename(url)
            out = files_dir / fname
            with sess.get(url, headers=headers, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(out, "wb") as fo:
                    for chunk in r.iter_content(1024 * 1024):
                        fo.write(chunk)
            design.files.append(FileAsset(filename=fname, path=str(out), url=url, sha256=sha256_file(out)))

        for imeta in images:
            url = imeta.get("url") or imeta.get("public_url") or (imeta.get("sizes", [{}])[-1].get("url") if imeta.get("sizes") else None)
            if not url:
                continue
            fname = os.path.basename(url.split("?")[0])
            out = images_dir / fname
            with sess.get(url, headers=headers, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(out, "wb") as fo:
                    for chunk in r.iter_content(1024 * 1024):
                        fo.write(chunk)
            design.images.append(ImageAsset(filename=fname, path=str(out), url=url))

        return design

    def write(self, design: Design, locator: str, *, mode: Literal["create", "update"]) -> str:
        if mode not in ("create", "update"):
            raise ValidationError("mode must be 'create' or 'update'")

        if mode == "create":
            # Clean and validate the payload
            description = (design.description_md or "").strip()
            instructions = (design.instructions_md or "").strip()
            tags = [tag.strip() for tag in (design.tags or []) if tag and tag.strip()]

            # Basic validation
            if not design.title or not design.title.strip():
                raise ValidationError("Design title is required")

            payload = {
                "name": design.title.strip(),
                "description": description if description else "A 3D design",
                "instructions": instructions if instructions else "Print with standard settings",
                "is_wip": False,
                "category": "other",  # Default category required by Thingiverse
            }

            # Only add tags if we have any
            if tags:
                payload["tags"] = tags

            # Normalize the license first
            normalized_license = normalize_license(design.license) if design.license else None
            lic_out = map_for_platform(normalized_license, "thingiverse")

            if lic_out:
                payload["license"] = lic_out
                LOGGER.debug("Using license '%s' mapped to '%s'",
                           normalized_license.key if normalized_license else "None", lic_out)
            else:
                # Thingiverse requires a license, default to CC-BY if none found
                LOGGER.warning("License '%s' not mapped to Thingiverse, using 'cc' as default",
                             design.license.key if design.license else "None")
                payload["license"] = "cc"
            LOGGER.debug("Creating thing with payload: %s", payload)
            created = self.api.create_thing(payload)
            thing_id = str(created.get("id"))
        else:
            thing_id = locator.strip()
            payload = {
                "name": design.title,
                "description": design.description_md,
                "instructions": design.instructions_md,
                "tags": design.tags,
            }
            lic_out = map_for_platform(design.license, "thingiverse")
            if lic_out:
                payload["license"] = lic_out
            self.api.update_thing(thing_id, payload)

        # Upload files via initiate + multipart + finalize
        LOGGER.debug(
            "Starting file upload process. Found %d files to upload", len(design.files)
        )
        for asset in design.files:
            path = Path(asset.path or "")
            if not path.is_file():
                continue
            LOGGER.debug("Uploading file: %s", asset.filename)

            # Step 1: Initiate upload
            try:
                LOGGER.debug(
                    "Initiating upload for %s (size: %d bytes)",
                    asset.filename,
                    path.stat().st_size,
                )
                init = self.api.initiate_file_upload(
                    thing_id, asset.filename, size=path.stat().st_size
                )
                LOGGER.debug("Upload initiation response: %s", init)
                upload_url = init.get("action")
                form_fields = init.get("fields") or {}
                success_redirect = form_fields.get("success_action_redirect")
                LOGGER.debug("Upload URL: %s", upload_url)
                LOGGER.debug("Form fields keys: %s", list(form_fields.keys()))
            except Exception as e:
                LOGGER.error("Failed to initiate upload for %s: %s", asset.filename, e)
                continue

            if not upload_url or not form_fields:
                LOGGER.warning(
                    "Upload initiation response missing required fields for %s",
                    asset.filename,
                )
                continue

            # Step 2: Upload file to S3
            with open(path, "rb") as file_handle:
                files = {
                    "file": (
                        asset.filename,
                        file_handle,
                        mimetypes.guess_type(asset.filename)[0]
                        or "application/octet-stream",
                    )
                }
                upload_resp = requests.post(
                    upload_url, data=form_fields, files=files, timeout=600
                )
                upload_resp.raise_for_status()
                LOGGER.debug("File upload to S3 completed for %s", asset.filename)

            # Step 3: Finalize upload with Thingiverse
            if success_redirect:
                finalize_resp = requests.post(
                    success_redirect,
                    headers=self.api._headers(),
                    data=form_fields,
                    timeout=120,
                )
                finalize_resp.raise_for_status()
                LOGGER.debug("File upload finalized for %s", asset.filename)
            else:
                LOGGER.warning(
                    "No success_action_redirect found for %s, upload may not be properly registered",
                    asset.filename,
                )

        # TODO: handle image uploads when API support is confirmed
        return thing_id
