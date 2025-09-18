from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

import requests

from ...exceptions import AuthenticationError, NotFoundError
from ...config import get_config

LOGGER = logging.getLogger("modpub.thingiverse.api")

class ThingiverseAPI:
    """Minimal Thingiverse API client.

    All requests are sent to https://api.thingiverse.com with OAuth2 Bearer tokens.
    """
    BASE = "https://api.thingiverse.com"

    def __init__(self, access_token: Optional[str] = None, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()
        # Priority: 1. Passed parameter, 2. Config system (env var, current dir, home dir)
        self.token = access_token
        if not self.token:
            config = get_config()
            self.token = config.get_thingiverse_token()
        if not self.token:
            raise AuthenticationError("THINGIVERSE_TOKEN not set; provide access_token, env var, or config file")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

    def _get(self, path: str, **kwargs) -> Any:
        url = self.BASE + path
        r = self.session.get(url, headers=self._headers(), timeout=60, **kwargs)
        if r.status_code == 404:
            raise NotFoundError(f"Not found: {url}")
        if r.status_code == 401:
            raise AuthenticationError("Unauthorized; check token")
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, json: Optional[dict] = None, **kwargs) -> Any:
        url = self.BASE + path
        r = self.session.post(url, headers=self._headers(), json=json, timeout=120, **kwargs)
        if r.status_code == 401:
            raise AuthenticationError("Unauthorized; check token")
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "")
        return r.json() if ctype.startswith("application/json") else r.text

    def _patch(self, path: str, json: dict) -> Any:
        url = self.BASE + path
        r = self.session.patch(url, headers=self._headers(), json=json, timeout=120)
        if r.status_code == 401:
            raise AuthenticationError("Unauthorized; check token")
        r.raise_for_status()
        return r.json()

    def get_thing(self, thing_id: str) -> Dict[str, Any]:
        return self._get(f"/things/{thing_id}")

    def get_thing_files(self, thing_id: str) -> List[Dict[str, Any]]:
        return self._get(f"/things/{thing_id}/files")

    def get_thing_images(self, thing_id: str) -> List[Dict[str, Any]]:
        return self._get(f"/things/{thing_id}/images")

    def get_thing_tags(self, thing_id: str) -> List[Dict[str, Any]]:
        return self._get(f"/things/{thing_id}/tags")

    def create_thing(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/things", json=payload)

    def update_thing(self, thing_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._patch(f"/things/{thing_id}", json=payload)

    def initiate_file_upload(self, thing_id: str, filename: str, size: int, md5: Optional[str] = None) -> Dict[str, Any]:
        payload = {"filename": filename, "size": size}
        if md5:
            payload["md5"] = md5
        return self._post(f"/things/{thing_id}/files", json=payload)
