"""Benjamini-Hochberg step-up correction for declared result families."""

from typing import Any

from readout_stats.cityflow_fdr import FDRResult as FDRResult
from readout_stats.cityflow_fdr import benjamini_hochberg as _cityflow_bh


def benjamini_hochberg(p_values: list[float], q: float = 0.05) -> list[float]:
    return _cityflow_bh(p_values, q).adjusted.tolist()  # type: ignore[no-any-return]


def correct(records: list[dict[str, Any]], q: float = 0.05) -> list[dict[str, Any]]:
    corrected = _cityflow_bh([r["p_value"] for r in records], q)
    return [
        {
            **r,
            "p_adjusted": float(p),
            "significant": r["p_value"] <= q,
            "significant_adjusted": bool(rejected),
            "fdr_q": q,
        }
        for r, p, rejected in zip(records, corrected.adjusted, corrected.rejected, strict=True)
    ]
