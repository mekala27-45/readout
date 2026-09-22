"""Re-render complete docs and readouts from committed relational evidence."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from readout_api.repository import Repository
from readout_render.renderer import publish

from scripts.restore_evidence import ROOT, restore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--database-url")
    args = parser.parse_args()
    with TemporaryDirectory(prefix="readout-claims-") as temporary:
        if args.database_url:
            url = args.database_url
        else:
            database = Path(temporary) / "evidence.db"
            restore(database)
            url = "sqlite:///" + database.as_posix()
        repository = Repository(url)
        try:
            errors = publish(repository, ROOT, write=args.write)
        finally:
            repository.close()
    if errors:
        raise SystemExit("\n\n".join(errors))
    print("Whole-file claim gate passed for docs, readouts and committed web bundle.")


if __name__ == "__main__":
    main()
