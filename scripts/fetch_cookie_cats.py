"""Fetch the public source without credentials and record byte provenance."""

import hashlib
import io
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
REF = "mursideyarkin/mobile-games-ab-testing-cookie-cats"


def main() -> None:
    target = ROOT / "experiments/cookie_cats"
    target.mkdir(parents=True, exist_ok=True)
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        metadata = client.get(f"https://www.kaggle.com/api/v1/datasets/view/{REF}")
        metadata.raise_for_status()
        response = client.get(f"https://www.kaggle.com/api/v1/datasets/download/{REF}")
        response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        matches = [name for name in archive.namelist() if Path(name).name == "cookie_cats.csv"]
        if len(matches) != 1:
            raise ValueError("Source archive must contain exactly one Cookie Cats CSV")
        data = archive.read(matches[0])
    (target / "cookie_cats.csv").write_bytes(data)
    provenance = {
        "source_url": f"https://www.kaggle.com/datasets/{REF}",
        "download_url": f"https://www.kaggle.com/api/v1/datasets/download/{REF}",
        "retrieved_at": datetime.now(UTC).isoformat(),
        "source_version": metadata.json()["currentVersionNumber"],
        "license_as_listed": metadata.json()["licenseName"],
        "license_note": "The description credits DataCamp and Tactile Entertainment but states no additional license grant. The data is not covered by this repository's Apache license.",
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }
    (target / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
