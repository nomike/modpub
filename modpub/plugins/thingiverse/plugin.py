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
from ...core.licenses import normalize_license, map_for_platform
from ...exceptions import ValidationError
from ..repository import RepositoryPlugin
from .api import ThingiverseAPI

LOGGER = logging.getLogger("modpub.thingiverse.plugin")

class ThingiversePlugin(RepositoryPlugin):
    """Thingiverse provider plugin (read/create/update)."""
    name = "thingiverse"

    def __init__(self) -> None:
        self.api = ThingiverseAPI()

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

        # Upload files via initiate + multipart
        for asset in design.files:
            path = Path(asset.path or "")
            if not path.is_file():
                continue
            init = self.api.initiate_file_upload(thing_id, asset.filename, size=path.stat().st_size)
            upload_url = init.get("upload_url") or init.get("url")
            form = init.get("form") or init.get("fields") or {}
            if not upload_url or not form:
                LOGGER.warning("Upload initiation response missing 'upload_url' or 'form' for %s", asset.filename)
                continue
            files = {
                "file": (asset.filename, open(path, "rb"), mimetypes.guess_type(asset.filename)[0] or "application/octet-stream"),
            }
            resp = requests.post(upload_url, data=form, files=files, timeout=600)
            resp.raise_for_status()

        # TODO: handle image uploads when API support is confirmed
        return thing_id
