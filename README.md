# Pyxle Demos

Three demo apps built with [Pyxle](https://pyxle.dev) — a Python-first full-stack web framework where server logic and React UI live in the same `.pyxl` file.

Each app is a few hundred lines of code. Each is live and interactive.

## The Demos

### [Flux](flux/) — SaaS Analytics Dashboard

> **Live:** [flux.pyxle.app](https://flux.pyxle.app)

A dark-themed analytics dashboard with MRR charts, customer CRUD, revenue forecasting, and a settings panel. Server-rendered from SQLite with data aggregation in Python.

**Pyxle features shown:** `@server` loaders, `@action` mutations, dynamic `[id]` routing, layout loaders (`layoutData`), `usePathname()` for active nav state.

---

### [Chroma](chroma/) — Color Palette Generator

> **Live:** [chroma.pyxle.app](https://chroma.pyxle.app)

A light-themed color tool with 18 curated palettes, interactive palette creation, and WCAG accessibility analysis. Color harmony algorithms (analogous, complementary, triadic, split-complementary, monochromatic) run server-side using Python's `colorsys` standard library.

**Pyxle features shown:** `@action` for server-side color computation, `@server` loaders, dynamic `[id]` routing, file-based routing, client-side filtering.

---

### [Glyph](glyph/) — Generative Geometric Art

> **Live:** [glyph.pyxle.app](https://glyph.pyxle.app)

A dark gallery of spirographs, rose curves, mandalas, star polygons, Lissajous curves, and wave patterns. Every SVG point is computed server-side with `math.sin` and `math.cos`, then rendered in React.

**Pyxle features shown:** `@action` for server-side geometry computation, pre-computed gallery via `@server`, parameter validation with `ActionError`, dynamic `[id]` routing.

---

### [Pulse](pulse/) — a full-stack reference app

> **Live:** [pulse.pyxle.app](https://pulse.pyxle.app)

**Pulse** is a fictional service-status page built to exercise *every* Pyxle feature in one real app — a status page, a live incident war room, a validated report form, and a "how it works" tour. Python loaders and React UI in the same `.pyxl` file, server-rendered and hydrated.

**Pyxle features shown:** file-based routing (static + dynamic), `@server` loaders, **ISR caching** & **static generation**, `@action` + **Pydantic** validation, `useAction`, `<Form>`, **WebSockets** (`pyxle.realtime` + `useWebSocket`), **background tasks**, **pyxle-db** (migrations + transactions), `error.pyxl`/`not-found.pyxl`/`loading.pyxl` boundaries, **Slots**, `<Image>`, `<Script>`, `<Head>`, `<Link>`, `navigate()`, `usePathname()`, `<ClientOnly>`, **observability** (Prometheus), **rate limiting**, and a custom **middleware**.

---

## Run Locally

Each demo is a standalone Pyxle app. Pick one and run:

```bash
# Install Pyxle
pip install pyxle-framework

# Pick a demo
cd flux    # or: cd chroma / cd glyph / cd pulse

# Install dependencies and start
npm install
pyxle dev
```

Open [http://localhost:8000](http://localhost:8000).

### Requirements

- Python 3.10+
- Node.js 18+
- npm

## What is Pyxle?

Pyxle lets you write Python server logic and React UI in a single `.pyxl` file:

```python
# pages/index.pyxl

@server
async def load(request):
    # This runs on the server (Python)
    return {"message": "Hello from Python"}

# --- React UI below ---

import React from 'react';

export default function Page({ data }) {
    return <h1>{data.message}</h1>;
}
```

- **Website:** [pyxle.dev](https://pyxle.dev)
- **Framework:** [github.com/pyxle-dev/pyxle](https://github.com/pyxle-dev/pyxle)
- **Docs:** [pyxle.dev/docs](https://pyxle.dev/docs)

## License

[MIT](LICENSE)
