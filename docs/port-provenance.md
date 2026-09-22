# Reused build components

The whole-document claim gate follows [cityflow's renderer](https://github.com/mekala27-45/cityflow/blob/2163b362d75458e8485f3f78fdec85b7322e6fd7/scripts/check_published_numbers.py): query-produced manifests, explicit formatting, complete-file re-rendering and readable diffs. Readout adapts it to strict Jinja templates, relational evidence and both Markdown and HTML product outputs. Frontdesk's independent relational evidence checks informed the persistence boundary.

The Benjamini-Hochberg result dataclass and algorithm are ported from [cityflow's FDR module](https://github.com/mekala27-45/cityflow/blob/2163b362d75458e8485f3f78fdec85b7322e6fd7/packages/stats/src/cityflow_stats/fdr.py), with a JSON adapter for readout's result records. The original color-separation validator is retained in `scripts/palette_core.cjs` and supplemented with semantic text contrast checks and an explicit fixed-palette exception report.

StrictModel preserves [trajectory's contract behavior](https://github.com/mekala27-45/trajectory/blob/51a8b62ef483623baed2b7b8eab744b636d3d576/packages/core/src/trajectory_core/models.py): reject extra fields, validate assignment, preserve string whitespace and permit computed-field serialization round trips. This project additionally requires strict input types and finite numeric values. The punctuation gate is adapted to scan source and readout templates while pruning dependency trees before traversal.

Pricepoint's original power assumptions, source calculation, elasticity discussion and results are included under `experiments/pricepoint`, with the source revision recorded in the generated result. Arithmetic reproduction preserves its log price contrast and measured residual scale.
