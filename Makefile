.PHONY: sync test quality calibrate rederive claims api web publish
sync:
	uv sync --frozen
test:
	uv run pytest --cov
quality:
	uv run ruff check .
	uv run mypy
	uv run python -m scripts.check_no_em_dash
calibrate:
	uv run python -m scripts.run_calibration
rederive:
	uv run python -m scripts.reset_and_rederive
claims:
	uv run python -m scripts.check_published_numbers
api:
	uv run uvicorn readout_api.app:app --host 127.0.0.1 --port 8000
web:
	cd web && npm run dev
publish: rederive quality test claims
	cd web && npm run build
