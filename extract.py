#!/usr/bin/env python3
"""Parse the EI Statistical Review workbook into a clean JSON dataset for the dashboard."""
import openpyxl, json, re, math

SRC = "/sessions/zealous-beautiful-hypatia/mnt/uploads/EI-Stats-Review-ALL-data (2).xlsx"
OUT = "/sessions/zealous-beautiful-hypatia/mnt/outputs/ei_data.json"

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)

# ---------- helpers ----------
def is_year(v):
    if isinstance(v, int) and 1850 <= v <= 2035:
        return True
    if isinstance(v, float) and v.is_integer() and 1850 <= v <= 2035:
        return True
    return False

def clean_num(v):
    """Return float (rounded) or None for non-numeric / na markers."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        # round to 6 sig figs to keep file small but lossless-enough
        if v == 0:
            return 0
        try:
            r = round(v, 6 - int(math.floor(math.log10(abs(v)))) - 1)
        except Exception:
            r = v
        if isinstance(r, float) and r.is_integer():
            return int(r)
        return r
    s = str(v).strip()
    if s in ("-", "–", "—", "", "n/a", "N/A", "na", "NA", "^", "*"):
        return None
    s2 = s.replace(",", "")
    try:
        f = float(s2)
        return int(f) if f.is_integer() else round(f, 4)
    except Exception:
        return None

def cell_str(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()

def norm_name(s):
    """Normalize an entity / series name: collapse whitespace, fix the one source typo,
    and strip trailing footnote digits/superscripts (e.g. 'India2' -> 'India')."""
    s = re.sub(r"\s+", " ", str(s)).strip()
    s = s.replace("Russian Federationeration", "Russian Federation")
    # strip trailing superscript footnote characters
    s = re.sub(r"[¹²³⁰-⁹\*\^]+$", "", s).strip()
    # strip a trailing footnote digit run if preceded by a letter (country names don't end in digits)
    m = re.match(r"^(.*[A-Za-z\)])\s?(\d{1,2})$", s)
    if m:
        s = m.group(1).strip()
    return s

AGG_PATTERNS = [
    r"^total\b", r"\btotal$", r"^of which", r"\boecd\b", r"non-oecd",
    r"european union", r"^eu\b", r"\bworld\b", r"^other\b", r"opec",
    r"cis$", r"^cis\b", r"rest of", r"middle east$", r"africa$",
    r"asia pacific$", r"europe$", r"north america$",
    r"s\. & cent\. america", r"central america$",
]
def is_aggregate(name):
    n = name.lower().strip()
    for p in AGG_PATTERNS:
        if re.search(p, n):
            return True
    return False

# ---------- category mapping ----------
def categorize(name):
    n = name.lower()
    if name in ("Contents", "Definitions", "Approximate conversion factors"):
        return "Reference"
    if "carbon price" in n or "co2" in n or "co2e" in n or "ccus" in n or "flaring" in n or "methane" in n:
        return "Carbon & Emissions"
    if (name.startswith("Oil") or "oil" in n.split() or "crude" in n or "spot crude" in n
            or n.startswith("ngls") or n.startswith("liquids") or "refin" in n):
        return "Oil"
    if name.startswith("Gas") or n.startswith("gas "):
        return "Natural Gas"
    if name.startswith("Coal"):
        return "Coal"
    if "nuclear" in n:
        return "Nuclear"
    if "hydro" in n:
        return "Hydro"
    if any(k in n for k in ["renewable", "solar", "wind", "geo biomass", "biofuel", "saf"]):
        return "Renewables"
    if "elec" in n:
        return "Electricity"
    if "bess" in n or "data centre" in n or "data center" in n:
        return "Storage & Demand"
    if any(k in n for k in ["cobalt", "lithium", "graphite", "rare earth", "copper", "manganese", "nickel", "zinc", "mineral commodity"]):
        return "Critical Minerals"
    if "total energy" in n or "tes" in n:
        return "Overview"
    return "Other"

CATEGORY_ORDER = ["Overview", "Carbon & Emissions", "Oil", "Natural Gas", "Coal",
                  "Nuclear", "Hydro", "Renewables", "Electricity", "Storage & Demand",
                  "Critical Minerals", "Other", "Reference"]

# ---------- per-sheet parse ----------
def load_grid(ws):
    rows = []
    for r in ws.iter_rows(values_only=True):
        rows.append(list(r))
    # trim fully-empty trailing rows/cols
    while rows and all(c is None for c in rows[-1]):
        rows.pop()
    if not rows:
        return []
    maxc = max((max((i for i, c in enumerate(r) if c is not None), default=-1) for r in rows), default=-1) + 1
    rows = [r[:maxc] for r in rows]
    return rows

def find_year_header_row(grid):
    """Return (row_idx, [(col_idx, year)...]) for the row with the most year cells, or None."""
    best = None
    for ri, row in enumerate(grid[:8]):
        yrs = [(ci, int(c)) for ci, c in enumerate(row) if is_year(c)]
        # require at least 2 years and that they are increasing-ish
        if len(yrs) >= 2:
            if best is None or len(yrs) > len(best[1]):
                best = (ri, yrs)
    return best

def parse_sheet(name, ws):
    grid = load_grid(ws)
    cat = categorize(name)
    title = ""
    for row in grid[:3]:
        for c in row:
            if c is not None and str(c).strip():
                title = str(c).strip()
                break
        if title:
            break

    out = {"name": name, "category": cat, "title": title, "type": "raw"}

    # Reference / contents -> raw only
    if cat == "Reference":
        out["grid"] = [[cell_str(c) for c in row] for row in grid]
        return out

    yh = find_year_header_row(grid)

    # ---- Year-indexed (prices): years run DOWN the first column ----
    col0_years = [r for r in range(len(grid)) if grid[r] and is_year(grid[r][0])]
    header_for_series = None
    if len(col0_years) >= 4 and (yh is None or len(col0_years) > len(yh[1])):
        # series headers: the last non-empty text row above first year row
        first_yr_row = col0_years[0]
        hdr_row_idx = None
        for r in range(first_yr_row - 1, -1, -1):
            texts = [ci for ci, c in enumerate(grid[r]) if c is not None and str(c).strip() and not is_year(c)]
            if len(texts) >= 2:
                hdr_row_idx = r
                break
        series = []
        ncols = max(len(grid[r]) for r in col0_years)
        for ci in range(1, ncols):
            label = ""
            if hdr_row_idx is not None and ci < len(grid[hdr_row_idx]):
                label = cell_str(grid[hdr_row_idx][ci])
            # combine multi-row header if needed
            if not label:
                for r in range(max(0, first_yr_row - 4), first_yr_row):
                    if ci < len(grid[r]) and cell_str(grid[r][ci]):
                        label = cell_str(grid[r][ci]); break
            series.append(label or f"Series {ci}")
        years = [int(grid[r][0]) for r in col0_years]
        seriesdata = []
        for ci in range(1, ncols):
            vals = []
            for r in col0_years:
                v = grid[r][ci] if ci < len(grid[r]) else None
                vals.append(clean_num(v))
            if any(v is not None for v in vals):
                seriesdata.append({"name": norm_name(series[ci-1]), "values": vals})
        unit = ""
        for r in range(first_yr_row):
            for c in grid[r]:
                if c and ("per " in str(c).lower() or "dollar" in str(c).lower() or "$" in str(c)):
                    unit = str(c).strip(); break
            if unit: break
        out.update({"type": "yearindexed", "years": years, "series": seriesdata, "unit": unit})
        out["grid"] = [[cell_str(c) for c in row] for row in grid]
        return out

    # ---- Standard timeseries: countries x years ----
    if yh is not None and len(yh[1]) >= 3:
        hr, yrs = yh
        # Keep ONLY the contiguous, strictly-increasing run of year columns starting
        # at the first year cell. Trailing cols whose header is also a year (e.g. a
        # "Growth rate ... 2025" or "Share 2025" column) break the run and become extras.
        run = [yrs[0]]
        for ci, y in yrs[1:]:
            pci, py = run[-1]
            if ci == pci + 1 and y == py + 1:
                run.append((ci, y))
            else:
                break
        year_cols = run
        years = [y for ci, y in year_cols]
        ycols = [ci for ci, y in year_cols]
        first_ycol = min(ycols)
        last_ycol = max(ycols)
        # unit = text in header row before years, or row above
        unit = ""
        for ci in range(first_ycol):
            if hr < len(grid) and ci < len(grid[hr]) and cell_str(grid[hr][ci]):
                unit = cell_str(grid[hr][ci]); break
        if not unit:
            for r in range(hr):
                if grid[r] and cell_str(grid[r][0]):
                    t = cell_str(grid[r][0])
                    if any(u in t.lower() for u in ["joule","tonne","barrel","cubic","watt","capita","megawatt","percent","%","kbo","mt","bcm","bcf","twh","ej","pj","gj"]):
                        unit = t; break
        # trailing extra columns (growth/share) - headers from hr row after last year col.
        # The descriptor (e.g. "Growth rate per annum") often sits in the row above and is
        # a merged cell, so carry it forward left-to-right across the extra region.
        ncol_total = max((len(grid[r]) for r in range(hr, len(grid))), default=0)
        extra_cols = []
        carry = ""
        for ci in range(last_ycol + 1, ncol_total):
            lbl = cell_str(grid[hr][ci]) if ci < len(grid[hr]) else ""
            above = ""
            for r in range(max(0, hr-2), hr):
                if ci < len(grid[r]) and cell_str(grid[r][ci]):
                    above = cell_str(grid[r][ci])
            if above:
                carry = above
            full = (carry + " " + lbl).strip() if carry else lbl
            full = re.sub(r"\s+", " ", full).strip()
            if full:
                extra_cols.append({"col": ci, "name": full})

        entities = []
        notes = []
        data_start = hr + 1
        for r in range(data_start, len(grid)):
            row = grid[r]
            label = cell_str(row[0]) if row else ""
            # detect footnotes (label starts with note markers or appears after data with no numbers)
            vals = []
            for ci in ycols:
                v = row[ci] if ci < len(row) else None
                vals.append(clean_num(v))
            has_num = any(v is not None for v in vals)
            if not label and not has_num:
                if entities:
                    entities[-1]["gapAfter"] = True
                continue
            if label and not has_num:
                # could be a footnote / note row, or a sub-header. Heuristic:
                low = label.lower()
                if (label[0] in "*^123456789♦" or low.startswith(("note","source","*","w/o","less than","n/a"))
                        or len(label) > 60):
                    notes.append(re.sub(r"\s+"," ", label).strip())
                    continue
                # else treat as a blank-data entity (rare) - skip
                continue
            extras = {}
            for ec in extra_cols:
                ev = row[ec["col"]] if ec["col"] < len(row) else None
                cv = clean_num(ev)
                if cv is not None:
                    extras[ec["name"]] = cv
            ent = {"name": norm_name(label), "values": vals}
            if is_aggregate(ent["name"]):
                ent["agg"] = True
            if extras:
                ent["extra"] = extras
            entities.append(ent)

        out.update({"type": "timeseries", "years": years, "unit": re.sub(r"\s+"," ", unit).strip(),
                    "entities": entities,
                    "extraCols": [e["name"] for e in extra_cols],
                    "notes": notes})
        return out

    # ---- fallback: raw grid (trade matrices, by-fuel, etc.) ----
    out["grid"] = [[cell_str(c) for c in row] for row in grid]
    return out

# ---------- run ----------
sheets = {}
order = []
for name in wb.sheetnames:
    ws = wb[name]
    try:
        parsed = parse_sheet(name, ws)
    except Exception as e:
        parsed = {"name": name, "category": categorize(name), "type": "raw",
                  "grid": [[cell_str(c) for c in row] for row in load_grid(ws)], "error": str(e)}
    sheets[name] = parsed
    order.append(name)

# group categories in order
cats = {}
for name in order:
    c = sheets[name]["category"]
    cats.setdefault(c, []).append(name)
categories = [{"name": c, "sheets": cats[c]} for c in CATEGORY_ORDER if c in cats]

data = {
    "meta": {
        "title": "Energy Institute Statistical Review of World Energy 2026",
        "source": "Energy Institute Statistical Review of World Energy (2026 edition)",
        "sheetCount": len(order),
    },
    "categories": categories,
    "order": order,
    "sheets": sheets,
}

with open(OUT, "w") as f:
    json.dump(data, f, separators=(",", ":"), ensure_ascii=False)

import os
size = os.path.getsize(OUT)
print(f"Wrote {OUT}  ({size/1e6:.2f} MB)")

# summary of types
from collections import Counter
tc = Counter(s["type"] for s in sheets.values())
print("Types:", dict(tc))
print("Categories:", {c["name"]: len(c["sheets"]) for c in categories})
# sanity: list timeseries sheets with year span + entity count
print("\nTimeseries sheets (sample):")
for name in order:
    s = sheets[name]
    if s["type"] == "timeseries":
        print(f"  {name[:34]:34s} yrs {s['years'][0]}-{s['years'][-1]} ({len(s['years'])})  entities={len(s['entities'])}  extra={len(s['extraCols'])}")
