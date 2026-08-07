# Meteocons icons

Sun and moon-phase icons used by the `--symbols icons` display mode
(sunrise → sun, sunset → the current moon phase).

Source: [Meteocons](https://github.com/basmilius/weather-icons) by Bas Milius,
licensed **MIT**. The SVGs were fetched via the Iconify API
(`https://api.iconify.design/meteocons/<name>.svg`) and rasterised to 512×512
PNG with `rsvg-convert` so the deploy host needs no SVG rasteriser at runtime.

The `-fill` (solid) variants are used — the outline versions are too faint at
display size. Files: `sunrise-fill` (sun over the horizon) plus the eight lunar
phases — `moon-new-fill`, `moon-waxing-crescent-fill`, `moon-first-quarter-fill`,
`moon-waxing-gibbous-fill`, `moon-full-fill`, `moon-waning-gibbous-fill`,
`moon-last-quarter-fill`, `moon-waning-crescent-fill`.

To refresh: re-fetch the SVGs and re-run
`rsvg-convert -w 512 -h 512 <name>.svg -o <name>.png`.
