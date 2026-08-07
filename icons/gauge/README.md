# Thermometer gauge icons

`--symbols icons` mode draws these on the left "min/max" box:

- `thermo-low.png` — an **empty** thermometer (bulb only) → the day's **low**.
- `thermo-high.png` — a **full** thermometer → the day's **high**.

They're loaded as monochrome silhouettes (via `weatherDisplay.mono_icon`) so
they take black or white to match the surrounding text, chosen by the
background brightness. Kept at their natural tall/narrow aspect (not square)
so `load_icon` scales them by height and the temperature can sit close beside.

Source: a plain black-on-white thermometer pair supplied by Sean; extracted to
transparent PNGs (alpha = darkness, tight-cropped).
