# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **research/content repository**, not a software project. It documents the official national technology strategies of 45 countries + the EU (46 "entities") across 8 fixed frontier-technology domains, plus an interactive visualization. There is **no build system, no tests, no linter, no package manager** — don't go looking for them. The deliverables are markdown files and a single self-contained `index.html`.

- `NN-Name.md` (01–46) — one profile per entity (e.g. `03-Japan.md`). Numbered by the order they were added (in batches), **not** alphabetical.
- `README.md` — overview + methodology (the repo's public face).
- `INDEX.md` — the full catalogue: per-batch country index tables, per-batch flagship-document matrices, and cross-cutting observations.
- `index.html` — the GitHub Pages site: an interactive maturity heatmap. Self-contained (vanilla CSS/JS, no dependencies/CDN).
- `LICENSE` — CC BY 4.0.

## The 8 domains are fixed and ordered

Every profile and the heatmap use the same eight domains in this exact order:

1. Nuclear energy · 2. Artificial intelligence · 3. Quantum information science · 4. Biomedical sciences / biotechnology · 5. Materials science (incl. critical minerals) · 6. Semiconductors / microelectronics · 7. Digital technology / infrastructure · 8. Autonomous systems

## Profile schema (match it exactly)

Each `NN-Name.md` follows one template — read any existing profile (e.g. `03-Japan.md`) before writing a new one:

1. `# {Entity} — National Technology Strategies (8 Domains)` heading
2. An italic source line: `*Source: Gemini deep research, 2026. ...*`
3. A 1-paragraph intro framing the entity's distinctive posture
4. A **Summary Table** (`Domain | Official Plan | Issuing Body | Year`) with all 8 rows
5. Eight numbered `## N. {Domain}` sections, each with bolded **Plan / Body / Year / URL / Summary** fields. The Summary is 3–6 sentences. Keep **official** source URLs (`.gov`/ministry/institutional); strip any `vertexaisearch.cloud.google.com` redirect links.

## Critical coupling: profiles ↔ heatmap ↔ index are maintained by hand

This is the main architectural gotcha. The heatmap's data is **not generated** from the profiles. `index.html` embeds a hand-authored `DATA` array where each entity has `d:[…]` — eight integers in the domain order above, encoding a **6-level posture scale**:

`-1` banned/phased-out · `0` absent · `1` nascent · `2` active · `3` mature · `4` frontier

(`-1` is a deliberate negative *choice*, e.g. nuclear bans — rendered red, not a low score.) These scores are an **editorial reading** of each strategy, not a derived metric. The distribution-bar footer in `index.html` is computed from this same array, so it updates automatically when `DATA` changes.

Adding or revising an entity therefore means editing **several files in lockstep**:
- the `NN-Name.md` profile
- the `DATA` array in `index.html` (correct region group + 8 posture codes)
- `INDEX.md` — its batch index table, the relevant flagship matrix, and any affected cross-cutting observations / entity counts
- `README.md` — the headline entity count if it changes

Entity links in `index.html` point to **GitHub blob URLs** via the `REPO_BASE` constant (so they render as markdown on github.com), not relative paths. If the repo owner/name changes, update `REPO_BASE` and the `toplinks`/Pages URLs.

## Research pipeline (how profiles are produced)

Profiles come from the **Gemini deep-research MCP tools**, not manual writing:
- `mcp__gemini__gemini-deep-research` to launch (prompt names the specific institutions, flagship programmes, and fault-lines to probe for that country), then `mcp__gemini__gemini-check-research` to poll by `researchId`. Runs ~5–20 min; poll on a cache-friendly cadence (e.g. `ScheduleWakeup` ~270s).
- Large results exceed tool token limits and are auto-saved to a `.txt` under the session's `tool-results/` dir — read them back in **chunks** with `Read` (`offset`/`limit`, ~150–175 lines) until 100% is read, then distil into the profile schema.

## Publishing

- Remote: `origin` → `github.com/curioputterings/national-technology-strategies`, default branch `main`. The active `gh` account is `curioputterings`.
- Commit identity is set **repo-local** to `curioputterings <curioputterings@proton.me>` (keeps the global gmail out of public history). End commit messages with the `Co-Authored-By: Claude …` trailer.
- GitHub Pages serves from `main` at root. `.nojekyll` is present so files are served as-is (no Jekyll build) — this is why `index.html` links to github.com blob URLs rather than relative `.md` (which Jekyll-off would serve as raw text).
- Preview the site locally with `python3 -m http.server` (then open `index.html`), or just open the file directly.
- After pushing, check the Pages build: `gh api /repos/curioputterings/national-technology-strategies/pages/builds/latest --jq .status` (look for `built`).
- Repo "About" (description/homepage/topics) is managed via `gh repo edit`.
