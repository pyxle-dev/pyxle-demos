# Chroma — Color Palette Generator

An interactive color tool built with [Pyxle](https://pyxle.dev), powered by Python's `colorsys` standard library.

**Live demo:** [chroma.pyxle.app](https://chroma.pyxle.app)

## Features

- 18 curated palettes across 6 moods (warm, cool, pastel, vibrant, earth, monochrome)
- Palette detail with full color analysis (RGB, HSL, WCAG contrast ratios, luminance)
- Create palettes from any base color using 5 harmony algorithms
- Color naming from HSL analysis
- Click-to-copy hex codes

## Python Standard Library in Action

All color science runs server-side using only Python's standard library:

- `colorsys` for HSL/RGB conversions and color harmony calculations
- `math` for relative luminance and WCAG contrast ratios
- No external dependencies for color computation

## Run

```bash
pip install pyxle-framework
npm install
pyxle dev
```

## Structure

```
pages/
  layout.pyxl        # Top navigation layout
  index.pyxl         # Home with featured palettes + random generator
  explore.pyxl       # Browse all palettes by mood
  palette/[id].pyxl  # Palette detail with accessibility table
  create.pyxl        # Interactive palette creator
colors.py            # Color science module (colorsys + math)
palettes.py          # Curated palette data
```
