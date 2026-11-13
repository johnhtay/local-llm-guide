# AGENTS.md: durable rules for agents working in this repo

Put here what used to live only in conversation, because long sessions drop
early instructions out of context (see chapter 04, "A real example of context
degradation"). Keep this file short enough that an agent actually re-reads it.

## Layout and tools

- All analysis scripts live in `scripts/`. Never add `.py` files to the repo
  root. When copying files into the repo, destination directories matter: scripts
  go to `scripts/`, beginner chapters to `beginner/`.
- Chapter tables are generated: `scripts/agg_task_types.py`, `scripts/mine_runtimes.py`,
  `scripts/mine_errors.py`, `scripts/mine_failures_by_model.py` regenerate them
  exactly. Do not hand-edit generated table cells; update the prose instead, or
  change the script.
- Charts come from `scripts/make_charts.py` (SVG plus 2x PNG). It anchors output
  to the repo root, so it works from any working directory.

## Content rules

- No em-dashes anywhere. Use commas, colons, periods.
- Every abbreviation is explained inline at first use AND has a glossary entry
  (glossary.md, beginner/glossary.md).
- Hardware prices: euro only, French retailers, checked date stated. Dollar
  MSRPs appear only as launch history; cloud prices stay in dollars.
- Reading times are reading-only (about 200 wpm plus table skim); never bundle
  install or run time into a chapter's time estimate.
- The README's "In one line" column and each chapter's closing
  `**Takeaway:**` box must stay consistent with the chapter's numbers.

## Verification

- Rebuild the PDF after content changes: the pandoc command is in README
  ("Printing" section), with `--resource-path=".:beginner"`; verify with PyMuPDF,
  not by eye.

