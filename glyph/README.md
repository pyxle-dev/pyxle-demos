# Glyph — Generative Geometric Art

A gallery of mathematical patterns built with [Pyxle](https://pyxle.dev), where every SVG point is computed server-side using Python's `math` module.

**Live demo:** [glyph.pyxle.app](https://glyph.pyxle.app)

## Features

- 12 pre-computed gallery patterns across 6 types
- Interactive pattern creator with parameter sliders
- Pattern detail pages with math facts and algorithm info
- 6 pattern algorithms: spirograph, rose curve, mandala, star polygon, Lissajous, wave interference

## Pattern Algorithms

All geometry is computed server-side with `math.sin` and `math.cos`:

- **Spirograph** — hypotrochoid curves from nested circular motion
- **Rose Curve** — polar curves defined by r = cos(k*theta)
- **Mandala** — radially symmetric petal patterns
- **Star Polygon** — regular stars with alternating inner/outer vertices
- **Lissajous** — two perpendicular harmonic oscillations
- **Wave Interference** — stacked sine waves at varying frequencies

## Run

```bash
pip install pyxle-framework
npm install
pyxle dev
```

## Structure

```
pages/
  layout.pyxl        # Dark gallery layout
  index.pyxl         # Pattern gallery with type overview
  pattern/[id].pyxl  # Pattern detail with math facts
  create.pyxl        # Interactive pattern creator
patterns.py          # Pattern algorithms + gallery data
```
