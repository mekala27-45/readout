# Cookie Cats provenance

Source: [Mobile Games A/B Testing: Cookie Cats](https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats), published by Murside Yarkin on Kaggle. The source credits DataCamp and the game's developer, Tactile Entertainment. This project is unaffiliated with those organizations.

Downloaded directly from the public Kaggle dataset API. The exact retrieval timestamp, source version, byte count and SHA checksum are recorded in [provenance.json](provenance.json). Re-fetch with `uv run python -m scripts.fetch_cookie_cats`.

Kaggle's license field reads **Other (specified in description)**. At retrieval, the description credited the original sources but supplied no additional license grant. We do not interpret that label as an open license or apply this project's Apache license to the CSV. Users should resolve reuse permissions with the original provider before redistribution beyond this attributed analytical demonstration.

Each row represents a randomized player installation, with assigned gate version, game rounds and retention indicators. The file contains no timestamps, pre-period covariates or record of actually reaching the gate. The readout is a retrospective analysis of public observations. Its locally registered design does not prove that the original team pre-registered it.
