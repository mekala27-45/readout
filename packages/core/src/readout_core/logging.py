"""JSON logging with raw unit identifiers removed before emission."""

from collections.abc import MutableMapping
from typing import Any

import structlog

from readout_core.hashing import hash_unit_id


def redact_unit_ids(
    _: Any, __: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    if "unit_id" in event_dict:
        event_dict["unit_id_hash"] = hash_unit_id(str(event_dict.pop("unit_id")))
    if "unit_ids" in event_dict:
        event_dict["unit_id_hashes"] = [
            hash_unit_id(str(unit)) for unit in event_dict.pop("unit_ids")
        ]
    return event_dict


def configure_logging() -> None:
    structlog.configure(processors=[redact_unit_ids, structlog.processors.JSONRenderer()])
