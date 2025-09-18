from __future__ import annotations
import logging
import re
import shutil
from pathlib import Path
from typing import Literal

from ...core.model import Design, FileAsset, ImageAsset
from ...core.storage import ensure_dir, sha256_file
from ...exceptions import ValidationError
from ..repository import RepositoryPlugin

LOGGER = logging.getLogger("modpub.localdir.plugin")

# README markers for robust round-trip
MD_DESC_BEGIN = "<!-- modpub:begin:description -->"
MD_DESC_END = "<!-- modpub:end:description -->"
MD_INSTR_BEGIN = "<!-- modpub:begin:instructions -->"
MD_INSTR_END = "<!-- modpub:end:instructions -->"
README_NAME = "README.md"

# Heuristic headings if markers are absent
_PRINT_INSTR_HEADINGS = [
    r"^##\s*print\s*instructions\s*$",
    r"^##\s*print\s*settings\s*$",
    r"^##\s*instructions\s*$",
    r"^##\s*printing\s*$",
]

def _render_readme(title: str, description: str, instructions: str) -> str:
    lines = []
    if title:
        lines.append(f"# {title}
")
    lines.append(MD_DESC_BEGIN)
    lines.append((description or '').rstrip() + "
")
    lines.append(MD_DESC_END + "
")
    lines.append("## Print Instructions
")
    lines.append(MD_INSTR_BEGIN)
    lines.append((instructions or '').rstrip() + "
")
    lines.append(MD_INSTR_END + "
")
    return "
".join(lines)

def _extract_between(text: str, start: str, end: str) -> str | None:
    s = text.find(start)
    if s == -1:
        return None
    s += len(start)
    e = text.find(end, s)
    if e == -1:
        return None
    return text[s:e].strip('
')

def _parse_readme(text: str) -> tuple[str, str]:
    # 1) Explicit markers
    desc = _extract_between(text, MD_DESC_BEGIN, MD_DESC_END)
    instr = _extract_between(text, MD_INSTR_BEGIN, MD_INSTR_END)
    if desc is not None or instr is not None:
        return (desc or "", instr or "")

    # 2) Heuristic heading split
    for pat in _PRINT_INSTR_HEADINGS:
        m = re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            start_instr = m.start()
            line_end = text.find('
', m.end())
            if line_end == -1:
                return (text[:start_instr].strip(), "")
            return (text[:start_instr].strip(), text[line_end+1:].strip())

    # 3) Fallback
    return (text.strip(), "")

class LocalDirPlugin(RepositoryPlugin):
    name = "localdir"

    def _root(self, locator: str) -> Path:
        return Path(locator).expanduser().resolve()

    def read(self, locator: str) -> Design:
        root = self._root(locator)
        meta = root / "metadata.json"
        if not meta.is_file():
            raise ValidationError(f"metadata.json not found in {root}")
        design = Design.from_json(meta.read_text(encoding="utf-8"))

        files_dir = root / "files"
        images_dir = root / "images"
        for f in design.files:
            if f.path:
                p = (root / f.path).resolve() if not Path(f.path).is_absolute() else Path(f.path)
            else:
                p = files_dir / f.filename
                f.path = str(p)
            if p.is_file():
                f.sha256 = sha256_file(p)
        for im in design.images:
            if im.path:
                p = (root / im.path).resolve() if not Path(im.path).is_absolute() else Path(im.path)
            else:
                p = images_dir / im.filename
                im.path = str(p)

        # README.md overrides
        readme_path = root / README_NAME
        if readme_path.is_file():
            desc_md, instr_md = _parse_readme(readme_path.read_text(encoding='utf-8'))
            if desc_md is not None:
                design.description_md = desc_md
            if instr_md is not None:
                design.instructions_md = instr_md
        return design

    def write(self, design: Design, locator: str, *, mode: Literal["create", "update"]) -> str:
        root = self._root(locator)
        ensure_dir(root)
        files_dir = root / "files"
        images_dir = root / "images"
        ensure_dir(files_dir)
        ensure_dir(images_dir)

        # Copy files/images
        new_files = []
        for f in design.files:
            src = Path(f.path) if f.path else None
            dst = files_dir / f.filename
            if src and src.is_file():
                if src.resolve() != dst.resolve():
                    shutil.copy2(src, dst)
                f.path = str(dst.relative_to(root))
                f.sha256 = sha256_file(dst)
            new_files.append(f)
        design.files = new_files

        new_images = []
        for im in design.images:
            src = Path(im.path) if im.path else None
            dst = images_dir / im.filename
            if src and src.is_file():
                if src.resolve() != dst.resolve():
                    shutil.copy2(src, dst)
                im.path = str(dst.relative_to(root))
            new_images.append(im)
        design.images = new_images

        # Write metadata & README
        (root / "metadata.json").write_text(design.to_json(), encoding='utf-8')
        (root / README_NAME).write_text(
            _render_readme(design.title, design.description_md, design.instructions_md),
            encoding='utf-8'
        )
        return str(root)
