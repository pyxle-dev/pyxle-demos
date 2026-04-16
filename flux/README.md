# Flux — SaaS Analytics Dashboard

A full-featured analytics dashboard built with [Pyxle](https://pyxle.dev).

**Live demo:** [flux.pyxle.app](https://flux.pyxle.app)

## Features

- Dashboard with KPI cards, MRR bar chart, and Python-computed revenue forecast
- Customer list with search and status filtering
- Customer detail with plan management via `@action`
- Settings page with form mutations
- Responsive sidebar layout with `usePathname()` active state
- Layout `@server` loader for shared data (`layoutData`)
- SQLite persistence with auto-seeding

## Stack

- **Server:** Python + Pyxle (`@server` loaders, `@action` mutations)
- **UI:** React 18 + Tailwind CSS
- **Database:** SQLite (auto-creates and seeds on first run)
- **Styling:** Dark theme

## Run

```bash
pip install pyxle-framework
npm install
pyxle dev
```

## Structure

```
pages/
  layout.pyxl       # Sidebar layout with @server loader
  index.pyxl        # Dashboard (KPIs, chart, activity feed)
  customers.pyxl    # Customer list with search
  customers/[id].pyxl  # Customer detail + plan change
  settings.pyxl     # Settings form
db.py               # SQLite data layer with seed data
```
