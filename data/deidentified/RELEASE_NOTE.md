# Disclosure review record

Dated decision record for this release, per the disclosure review checklist in
`data/deidentified/README.md`. Decisions by John H. Tay, 2026-11-13.

- Snapshot unchanged: the published files are byte-identical to the build
  output. Every file matches the `output_sha256` values in `manifest.json`;
  nothing was rounded or suppressed after the fact.
- Small strata kept: the two public free-tier sessions (41 tool calls, zero
  failures) remain in the data. Their existence is already published in the
  manuscript and in `manifest.json`, and the tier is combined with public
  cloud in every reported rate, so the stratum adds no further detail.
- `personal_admin` category kept: 23 sessions carry this broad task-group
  label. The derivative contains no titles, paths, commands or text, so the
  label discloses only the nature of the work, not its content.
- `human_correction` field kept: it is the rule-based language heuristic,
  approximate and never manually adjudicated. The field dictionary states
  this, and the manuscript does not report the field as ground truth.
- Month-granularity dates, durations and token totals reviewed and kept: the
  manuscript's published aggregates match this snapshot, and no field below
  month precision is present.
- The guide's chapter 09 session table was generalized for this release
  (personal names replaced with neutral task descriptions). That table is a
  part of the guide, not of this derivative; the derivative never contained
  titles. Day-level dates in that table are an accepted residual risk,
  recorded here rather than silently removed.
