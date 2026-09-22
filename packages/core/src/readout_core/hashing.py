"""Canonical content hashes and privacy-safe identifiers."""

import hashlib
import json
from typing import Any


def content_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def hash_unit_id(unit_id: str) -> str:
    return hashlib.sha256(unit_id.encode("utf-8")).hexdigest()
