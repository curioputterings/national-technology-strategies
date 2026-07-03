#!/usr/bin/env python3
"""
extract_plans.py — turn the hand-written national-tech-plans corpus into a
machine-readable (entity, domain, has_plan, year, posture, ...) table.

Why this exists
---------------
This repo is content, not software: 46 country profiles (`NN-Name.md`) plus a
hand-authored heatmap in `index.html`. Downstream projects in the workspace want
these facts as data, not prose:
  - grow_complexity/build_policy_alignment.py currently reads a *separate*,
    hand-authored data/policy_priorities.json — this table can replace it.
  - consumption_research_link/src/stage5_roadmap_link.py fills a `plan` column
    heuristically — this table gives it (country, domain, has_plan, year).

It fuses the two sources the repo already maintains in lockstep:
  - the per-file **Summary Table** (Domain | Official Plan | Issuing Body | Year)
    → the named plan, issuing body, and year per domain
  - the `DATA` array in **index.html** → the editorial 6-level posture code
    (-1 banned … 4 frontier) per domain

Both are positional over the same fixed 8-domain order (see DOMAINS below), so
they join by index. The markdown domain label is kept as `domain_raw` so any
drift between the two sources is auditable rather than silent.

Pure stdlib. Reads nothing outside this repo. Writes:
  data/national_plans.csv   (human-inspectable, one row per entity×domain)
  data/national_plans.json  (machine, nested by entity)
  data/national_plans.meta.json  (provenance: source files, counts, warnings)

Run:  python3 tools/extract_plans.py            # from repo root
      python3 tools/extract_plans.py --check    # parse + validate, write nothing
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO / "index.html"
OUT_DIR = REPO / "data"

# The eight fixed domains, in the canonical order used by every profile's
# Summary Table AND by the `d:[…]` posture arrays in index.html. Source of
# truth is the DOMAINS array in index.html; this mirror lets us run even if the
# HTML parse of the legend fails, and defines the join order.
CANON_DOMAINS = [
    "Nuclear energy",
    "Artificial intelligence",
    "Quantum information science",
    "Biomedical & biotechnology",
    "Materials & critical minerals",
    "Semiconductors",
    "Digital infrastructure",
    "Autonomous systems",
]

# posture code -> short status label (mirrors LV in index.html)
POSTURE_LABEL = {
    -1: "banned/phased-out",
    0: "absent",
    1: "nascent",
    2: "active",
    3: "mature",
    4: "frontier",
}

# Entity name -> ISO-3166 alpha-3, so the artifact joins directly onto the
# iso3-keyed projects (grow_complexity, consumption_research_link). Non-country
# entities use their conventional code: EU -> EUU (World Bank), Taiwan -> TWN.
NAME_TO_ISO3 = {
    "United States": "USA", "Canada": "CAN", "Mexico": "MEX",
    "China": "CHN", "Japan": "JPN", "South Korea": "KOR", "Taiwan": "TWN",
    "India": "IND", "Kazakhstan": "KAZ",
    "Singapore": "SGP", "Malaysia": "MYS", "Indonesia": "IDN", "Thailand": "THA",
    "Vietnam": "VNM", "Philippines": "PHL", "Brunei": "BRN", "Cambodia": "KHM",
    "Laos": "LAO", "Myanmar": "MMR",
    "Australia": "AUS", "New Zealand": "NZL",
    "Germany": "DEU", "France": "FRA", "United Kingdom": "GBR",
    "Netherlands": "NLD", "Italy": "ITA", "Spain": "ESP", "Ireland": "IRL",
    "Switzerland": "CHE",
    "Sweden": "SWE", "Finland": "FIN", "Norway": "NOR", "Poland": "POL",
    "Ukraine": "UKR",
    "European Union": "EUU",
    "Israel": "ISR", "United Arab Emirates": "ARE", "Saudi Arabia": "SAU",
    "Qatar": "QAT", "Turkey": "TUR", "Türkiye": "TUR",
    "Brazil": "BRA", "Argentina": "ARG", "Chile": "CHL",
    "South Africa": "ZAF", "Nigeria": "NGA", "Egypt": "EGY", "Oman": "OMN",
}

# Plan-cell text that means "no named plan" rather than an actual programme.
# Note: a deliberate ban/phase-out IS a plan (Australia's nuclear moratorium,
# Spain's PNIEC phase-out) — those name a real policy and stay has_plan=true.
# What counts as *no* plan is an explicit absence marker or a "no … plan" phrase.
_NO_PLAN_MARKERS = {"", "none", "n/a", "na", "-", "—", "–", "tbd",
                    "none identified", "absent", "nascent", "nascent / absent",
                    "nascent/absent", "explicitly absent"}
_NO_PLAN_SUBSTR = ("no dedicated", "no national", "no formal", "no official",
                   "lacks a", "no standalone", "no unified", "none (",
                   "explicitly absent")
# "no civil power plan", "no dedicated plan", "no unified plan", ...
_NO_PLAN_RE = re.compile(r"\bno\b[^.]*\bplan\b", re.I)


def _norm(s: str) -> str:
    return " ".join(s.split()).strip()


# --------------------------------------------------------------------------- #
# index.html parsing: DOMAINS legend + DATA entity rows (name, file, posture)  #
# --------------------------------------------------------------------------- #
def parse_index_html(text: str):
    """Return (domains, entities). entities: list of dicts n/f/d(list[int])."""
    # DOMAINS = [ ["Nuc","Nuclear energy"], ... ]
    dom_block = re.search(r"const DOMAINS\s*=\s*\[(.*?)\];", text, re.S)
    domains = CANON_DOMAINS
    if dom_block:
        pairs = re.findall(r'\[\s*"[^"]+"\s*,\s*"([^"]+)"\s*\]', dom_block.group(1))
        if len(pairs) == 8:
            domains = [_norm(p) for p in pairs]

    # entity rows: {n:"United States", f:"01-United-States.md", d:[4,4,...]}
    entities = []
    for m in re.finditer(
        r'\{\s*n:\s*"([^"]+)"\s*,\s*f:\s*"([^"]+)"\s*,\s*d:\s*\[([\-0-9,\s]+)\]\s*\}',
        text,
    ):
        name, fname, darr = m.group(1), m.group(2), m.group(3)
        codes = [int(x) for x in re.findall(r"-?\d+", darr)]
        entities.append({"name": _norm(name), "file": fname.strip(), "posture": codes})
    return domains, entities


# --------------------------------------------------------------------------- #
# Per-file Summary Table parsing                                              #
# --------------------------------------------------------------------------- #
def _split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def parse_summary_table(md_text: str):
    """Return list of (domain_raw, plan, body, year_raw) from the Summary Table.

    Robust to header spelling ('Issuing Agency' vs 'Issuing Body') and to the
    table sitting under a '## Summary Table' heading. Aligns columns by header.
    """
    lines = md_text.splitlines()
    # locate the header row: a pipe row containing 'Domain' and 'Year'
    hdr_idx = None
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("|") and "Domain" in ln and "Year" in ln:
            hdr_idx = i
            break
    if hdr_idx is None:
        return []
    header = [h.lower() for h in _split_row(lines[hdr_idx])]

    def col(*names, default=None):
        for nm in names:
            for j, h in enumerate(header):
                if nm in h:
                    return j
        return default

    c_dom = col("domain", default=0)
    c_plan = col("plan", default=1)
    c_body = col("agency", "body", "issuing", default=2)
    c_year = col("year", default=len(header) - 1)

    rows = []
    # data rows start after the header + separator row (|---|---|)
    for ln in lines[hdr_idx + 1:]:
        s = ln.strip()
        if not s.startswith("|"):
            break  # table ended
        if set(s) <= set("|-: "):
            continue  # separator row
        cells = _split_row(ln)
        if len(cells) < 2:
            continue
        get = lambda k: cells[k] if k is not None and k < len(cells) else ""
        rows.append((
            _norm(get(c_dom)), _norm(get(c_plan)),
            _norm(get(c_body)), _norm(get(c_year)),
        ))
    return rows


def extract_year(cell: str):
    """Latest 4-digit year (1900-2099) in the cell, or None. '2023/2025' -> 2025."""
    yrs = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", cell)]
    return max(yrs) if yrs else None


def has_plan(plan_cell: str, posture: int | None) -> bool:
    # strip markdown emphasis so "*Explicitly absent*" is recognised
    p = plan_cell.strip().strip("*_ ").strip().lower()
    if p in _NO_PLAN_MARKERS:
        return False
    if any(sub in p for sub in _NO_PLAN_SUBSTR):
        return False
    if _NO_PLAN_RE.search(p):
        return False
    return bool(p)


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #
def build():
    text = INDEX_HTML.read_text(encoding="utf-8")
    domains, entities = parse_index_html(text)
    warnings: list[str] = []

    long_rows = []          # flat rows for CSV
    nested: dict[str, dict] = {}

    for ent in entities:
        name, fname, posture = ent["name"], ent["file"], ent["posture"]
        md_path = REPO / fname
        if not md_path.exists():
            warnings.append(f"{name}: profile file missing ({fname})")
            table = []
        else:
            table = parse_summary_table(md_path.read_text(encoding="utf-8"))

        if len(posture) != 8:
            warnings.append(f"{name}: posture array has {len(posture)} codes (expected 8)")
        if table and len(table) != 8:
            warnings.append(f"{name}: summary table has {len(table)} rows (expected 8)")

        iso3 = NAME_TO_ISO3.get(name)
        if iso3 is None:
            warnings.append(f"{name}: no ISO3 mapping (iso3 left blank)")

        dom_records = []
        for i, domain in enumerate(domains):
            post = posture[i] if i < len(posture) else None
            row = table[i] if i < len(table) else ("", "", "", "")
            domain_raw, plan, body, year_raw = row
            year = extract_year(year_raw)
            rec = {
                "entity": name,
                "iso3": iso3 or "",
                "file": fname,
                "domain": domain,
                "domain_raw": domain_raw,
                "has_plan": has_plan(plan, post),
                "plan": plan,
                "issuing_body": body,
                "year": year,
                "year_raw": year_raw,
                "posture": post,
                "posture_label": POSTURE_LABEL.get(post, "") if post is not None else "",
            }
            dom_records.append(rec)
            long_rows.append(rec)

        nested[name] = {
            "iso3": iso3 or None,
            "file": fname,
            "domains": {r["domain"]: {
                "has_plan": r["has_plan"], "plan": r["plan"],
                "issuing_body": r["issuing_body"], "year": r["year"],
                "posture": r["posture"], "posture_label": r["posture_label"],
                "domain_raw": r["domain_raw"],
            } for r in dom_records},
        }

    meta = {
        "generator": "tools/extract_plans.py",
        "source_index_html": "index.html",
        "n_entities": len(entities),
        "n_rows": len(long_rows),
        "domains": domains,
        "posture_scale": POSTURE_LABEL,
        "warnings": warnings,
    }
    return long_rows, nested, meta


def write_outputs(long_rows, nested, meta):
    OUT_DIR.mkdir(exist_ok=True)
    cols = ["entity", "iso3", "file", "domain", "domain_raw", "has_plan",
            "plan", "issuing_body", "year", "year_raw", "posture", "posture_label"]
    csv_path = OUT_DIR / "national_plans.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in long_rows:
            w.writerow({k: ("" if r[k] is None else r[k]) for k in cols})
    (OUT_DIR / "national_plans.json").write_text(
        json.dumps(nested, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_DIR / "national_plans.meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return csv_path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="parse and validate, but write no output files")
    args = ap.parse_args()

    long_rows, nested, meta = build()

    print(f"entities: {meta['n_entities']}  rows: {meta['n_rows']}  "
          f"domains: {len(meta['domains'])}")
    with_plan = sum(1 for r in long_rows if r["has_plan"])
    with_year = sum(1 for r in long_rows if r["year"])
    print(f"has_plan=true: {with_plan}/{meta['n_rows']}   with year: {with_year}/{meta['n_rows']}")
    if meta["warnings"]:
        print(f"warnings ({len(meta['warnings'])}):")
        for w in meta["warnings"]:
            print(f"  - {w}")
    else:
        print("no warnings.")

    if args.check:
        print("--check: no files written.")
        return 0

    csv_path = write_outputs(long_rows, nested, meta)
    print(f"wrote {csv_path.relative_to(REPO)}, national_plans.json, national_plans.meta.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
