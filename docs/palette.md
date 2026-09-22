# Fixed palette and inherited validation

The original cityflow palette validator is preserved in `scripts/palette_core.cjs`, from upstream commit `2163b362d75458e8485f3f78fdec85b7322e6fd7`. The wrapper checks semantic text contrast and runs the inherited OKLab, chroma, lightness, graphical contrast and color-vision-deficiency checks against both page and panel surfaces in both themes.

The requested dark control `#94A3B8` and treatment `#0891B2` have a worst-case protanopia separation of 7.7, below the inherited floor of 8. The same pair fails on both dark surfaces. The fixed hues take precedence; the raw failures and upstream exit codes remain in `artifacts/palette-validation.json`. The light pair passes all inherited checks. This is one documented mandated-palette exception, not an unqualified pass.

CI invokes `node scripts/validate_palette.js --allow-mandated-palette-exception`. This bounded exception succeeds only when the exact known pair is the only failing pair and the UI retains dashed lines, hollow markers, named legends, and table views. Any new failure still rejects validation. Calling the wrapper without the explicit flag preserves the nonzero failure status.

The tertiary chart color `#D97706` passes all pairwise checks in both themes. Status is written as an icon and word; no diverging color ramp is used. All body and status text uses independently checked high-contrast tokens, and cyan buttons use a dark foreground.
