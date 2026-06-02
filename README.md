# National Technology Strategies — 46 Entities × 8 Frontier Domains

An open reference mapping the **official national strategies, plans, laws and policies** that 45 countries + the European Union pursue across eight frontier-technology domains — and how they compare.

**🔗 Live interactive heatmap:** https://curioputterings.github.io/national-technology-strategies/
**📚 Full catalogue (country index, flagship matrices, cross-cutting analysis):** [INDEX.md](INDEX.md)

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=flat-square&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/curioputterings)

---

## What this is

For every entity, all eight domains are documented to the same template — **official document name · issuing body · year · authoritative source URL · a goals/funding/targets summary**:

> Nuclear energy · Artificial intelligence · Quantum information science · Biomedical sciences / biotechnology · Materials science (incl. critical minerals) · Semiconductors / microelectronics · Digital technology / infrastructure · Autonomous systems (AVs, robotics, drones)

Coverage spans every inhabited continent: all of OECD, China, **all 10 ASEAN member states**, India, the EU supranational level, the Gulf, major emerging economies, Nordic/CEE, MENA-Africa, Latin America, Central Asia, a country at war (Ukraine), and the Pacific.

## The methodology — and why it's more involved than it looks

What reads as a tidy table is the output of a deliberately structured research pipeline. The complexity lives in four places:

**1. Scale.** 46 entities × 8 domains = **368 distinct domain-level analyses**. Each is a self-contained mini-study with its own primary document, issuing body, date, source link, and synthesis — not a sentence scraped from an index.

**2. Deep research per entity.** Every country was investigated with **Gemini deep research** — an autonomous agent that plans an approach, searches the open web, reads and cross-checks sources, and synthesises a long report (typically 5–20 minutes of live research per country). The agent was steered with a domain-specific prompt naming the institutions, flagship programmes and known fault-lines to probe (e.g. a given country's nuclear regulator, sovereign-LLM project, critical-minerals regime, drone authority), so the output is grounded rather than generic.

**3. A real extraction-and-normalisation pipeline.** Results were processed **one entity at a time** through a long-running, resumable loop: launch research → poll for completion on a cache-friendly cadence → handle oversized reports (the largest exceeded token limits and were read back in chunks) → strip search-redirect links and keep the *official* `.gov`/ministry URLs → distil to the fixed 8-field template → write one markdown profile. Repeated 46 times across nine batches.

**4. Cross-entity synthesis.** Beyond the per-country files, the corpus is read *across* entities: per-batch **flagship-document matrices** (every entity's headline policy per domain, side by side) and a set of **cross-cutting observations** — the global nuclear revival and its fault line, sovereign-LLM and post-quantum-crypto patterns, the "new-oil" critical-minerals scramble, resource-nationalism-vs-FDI splits, war as a tech accelerant, and more.

**5. From prose to picture.** For the [interactive heatmap](https://curioputterings.github.io/national-technology-strategies/), all 368 cells were scored on a six-level **posture scale** — `banned/phased-out → absent → nascent → active → mature → frontier` — so the structure becomes legible at a glance (digital and AI are near-universal; quantum and semiconductors are sparse with bright spots; nuclear reads as a diverging fault line). This scoring is an **editorial reading** of each strategy's ambition, funding and maturity — not a measured index.

## Caveats

- Summaries are **AI-assisted research syntheses**. Verify exact figures and current document versions against the cited official sources before relying on them.
- Several documents carry **2025/2026 dates** that may be drafts, forthcoming, or announced-but-not-finalised — confirm publication status.
- Some links point to official portals/landing pages rather than direct PDFs; some are non-English.
- The heatmap's cell scores are interpretive, as noted above.

## Repository layout

```
README.md          – this file (overview + methodology)
INDEX.md           – full catalogue: country index, flagship matrices, cross-cutting observations
index.html         – interactive maturity heatmap (the GitHub Pages site)
LICENSE            – CC BY 4.0
01-United-States.md … 46-New-Zealand.md   – the 46 per-entity profiles
```

## License

© 2026 curioputterings. The **summaries, the catalogue, and the visualisation** in this repository are licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](LICENSE) — you're free to share and adapt them, including commercially, as long as you give appropriate credit and link to this repository.

Note: the license covers *this compilation and its original summaries/analysis*. The underlying official strategies, plans, and laws are the property of their respective governments and institutions; consult the cited source for their terms.

## How to cite / attribution

CC BY 4.0 just asks for credit. If you use or adapt this work, please attribute it — copy whichever format fits:

**Plain text**
```
"National Technology Strategies — 46 Entities × 8 Frontier Domains" by curioputterings,
licensed under CC BY 4.0. Source: https://github.com/curioputterings/national-technology-strategies
```

**Markdown**
```markdown
["National Technology Strategies — 46 Entities × 8 Frontier Domains"](https://github.com/curioputterings/national-technology-strategies) by [curioputterings](https://github.com/curioputterings) is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
```

**HTML**
```html
<a href="https://github.com/curioputterings/national-technology-strategies">National Technology Strategies — 46 Entities × 8 Frontier Domains</a> by curioputterings is licensed under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
```

**BibTeX**
```bibtex
@misc{curioputterings2026nattech,
  title        = {National Technology Strategies across 8 Frontier Domains for 45 Countries and the EU},
  author       = {{curioputterings}},
  year         = {2026},
  howpublished = {\url{https://github.com/curioputterings/national-technology-strategies}},
  note         = {Licensed under CC BY 4.0}
}
```

When adapting (rescoring, re-summarising, building on the data), please note that changes were made.

## Support

If this is useful to you, you can support the work here:

☕ **[Buy me a coffee](https://www.buymeacoffee.com/curioputterings)**

## Contact

📧 **curioputterings@proton.me**

---

*Research compiled with Gemini deep research (2026). Shared for research and reference.*
