from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import json

@dataclass
class Author:
    """Author/creator of the design."""
    name: str
    url: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class License:
    """License for the design (canonicalized if possible)."""
    key: str
    name: Optional[str] = None
    url: Optional[str] = None

@dataclass
class FileAsset:
    """Design file (STL/SCAD/3MF/etc.)."""
    filename: str
    path: Optional[str] = None  # local path relative or absolute
    url: Optional[str] = None   # remote URL if any
    sha256: Optional[str] = None
    kind: str = "model"         # model|source|doc|other
    description: Optional[str] = None

@dataclass
class ImageAsset:
    """Image/photo/render asset."""
    filename: str
    path: Optional[str] = None
    url: Optional[str] = None
    caption: Optional[str] = None
    sha256: Optional[str] = None

@dataclass
class Derivative:
    """Link to an upstream model this is derived from."""
    source_url: str
    source_platform: Optional[str] = None
    source_id: Optional[str] = None

@dataclass
class Design:
    """Canonical internal representation of a 3D design/model."""
    title: str
    description_md: str = ""
    instructions_md: str = ""
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    license: Optional[License] = None
    author: Optional[Author] = None
    files: List[FileAsset] = field(default_factory=list)
    images: List[ImageAsset] = field(default_factory=list)
    derivatives: List[Derivative] = field(default_factory=list)
    platform: Optional[str] = None
    platform_id: Optional[str] = None
    public_url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    @staticmethod
    def from_json(s: str) -> "Design":
        data = json.loads(s)
        if (lic := data.get("license")):
            data["license"] = License(**lic)
        if (auth := data.get("author")):
            data["author"] = Author(**auth)
        data["files"] = [FileAsset(**x) for x in data.get("files", [])]
        data["images"] = [ImageAsset(**x) for x in data.get("images", [])]
        data["derivatives"] = [Derivative(**x) for x in data.get("derivatives", [])]
        return Design(**data)
