# Statistical Review of World Energy — Interactive Dashboard

An interactive, single-file HTML dashboard built from the **2026 Energy Institute Statistical Review of World Energy** "all data" workbook (97 tables: every fuel, emissions, prices, electricity, and critical minerals).

Open `EI-Statistical-Review-Dashboard.html` in any browser — no server, no install, all data embedded.

## What it does

- **Category navigation** down the left side — all 97 tables grouped into Overview, Carbon & Emissions, Oil, Natural Gas, Coal, Nuclear, Hydro, Renewables, Electricity, Storage & Demand, Critical Minerals, and Reference. Search box filters the list.
- **Compare over time** — pick any metric, overlay any set of countries/regions on a line chart, set the year range, download the selection as CSV. Quick presets: Top 8, Regions, World.
- **Latest-year ranking** — sorted bar chart of who's biggest in any year, with share-of-world and the growth/CAGR columns from the workbook. Toggle countries-only vs. including regional totals.
- **Data table** — the full faithful table, sortable by clicking any year column, row filter, CSV download.
- **Country profile** — pick one country/region and see its latest value across every metric, with sparklines; click a card to jump to its full chart.
- Light/dark toggle.

## Publishing to GitHub Pages

1. Put `EI-Statistical-Review-Dashboard.html` in a repo and **rename it to `index.html`** (or, in the repo, Settings → Pages → set the source and point to the file).
2. Enable GitHub Pages on the `main` branch / root.
3. The dashboard loads Chart.js from a CDN, so it needs internet to render charts (true on GitHub Pages). All energy data is embedded in the file itself.

## Regenerating from a new edition

When a new annual workbook is released:

1. `python3 extract.py` — parses the `.xlsx` into `ei_data.json` (edit the `SRC` path at the top).
2. `python3 build_html.py` — embeds the JSON and writes the dashboard HTML.

The parser auto-classifies each sheet (time series / price series / matrix-or-reference), so it should handle next year's edition with little or no change.

## Files

| File | Purpose |
|------|---------|
| `EI-Statistical-Review-Dashboard.html` | The dashboard (open this) |
| `ei_data.json` | Extracted data (embedded in the HTML; kept separately for reference) |
| `extract.py` | Workbook → JSON parser |
| `build_html.py` | JSON → dashboard builder |

Source: Energy Institute, *Statistical Review of World Energy* (2026). Data © Energy Institute.
