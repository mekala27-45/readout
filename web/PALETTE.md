# Palette validation

`scripts/palette_core.cjs` is the original cityflow validator from commit `2163b362d75458e8485f3f78fdec85b7322e6fd7`. The wrapper `scripts/validate_palette.js` adds normal-text contrast checks and runs the original categorical checks against the page and panel surfaces in both themes. Its JSON report is committed under `artifacts/`.

The mandated dark control and treatment hues fail one inherited criterion: worst color-vision-deficiency OKLab separation is 7.7 for protanopia against a floor of 8. The raw failure remains visible in the JSON and the validator exits nonzero by default. CI explicitly supplies `--allow-mandated-palette-exception`, which accepts only these known dark-surface failures and verifies redundant encodings. Any other failure still fails validation. Both colors meet the graphical contrast threshold, and the light-mode pair passes all inherited checks. This is a documented exception for conflicting fixed-hue requirements, not an unqualified accessibility pass.

The interface provides additional line patterns, marker shapes, direct labels, status icons with words, and a table view alongside every chart. The tertiary chart color is `#D97706`; its pairs pass the inherited checks in both themes. No diverging color ramp is used. Text uses separate high-contrast semantic tokens, including the dark foreground on cyan action buttons.
