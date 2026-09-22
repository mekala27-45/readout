"""Run the independent Monte Carlo studies and persist their measured records."""

import json

from readout_api.repository import Repository
from readout_calibrate.harness import run_calibration


def main() -> None:
    repository = Repository()
    try:
        result = run_calibration(full=True)
        repository.save_calibration(result)
        print(
            json.dumps(
                {
                    "peeking_final": result["peeking"][-1],
                    "power": result["power"],
                    "srm": result["srm"],
                    "pricepoint": result["pricepoint"],
                },
                indent=2,
            )
        )
    finally:
        repository.close()


if __name__ == "__main__":
    main()
