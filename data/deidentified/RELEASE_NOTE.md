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
- Additional title generalization (2026-11-13): personal-finance topics
  (a listed energy company, household asset work, public-finance research,
  a salary calculation), tooling-experiment rows and device/purchase details
  now display as neutral labels ("Investment research", "Tooling experiment",
  "Mobile SIM troubleshooting", and so on). One prose paragraph in chapter 09
  was generalized to match. The classifier keywords that produce these
  categories remain in the published scripts: they are the method's
  definition of the personal-admin and non-work categories, and changing them
  would alter the published work/home split. They name topics, not people.
- Token accounting: the guide's chapter 09 Gen tok column uses per-message
  token sums at the same cutoff, matching this derivative. OpenCode's
  session-level ledger columns can read slightly higher for the same
  sessions; the difference is an accounting-basis difference, not missing
  data, and both bases are documented in the scripts.
- Manifest refreshed (2026-11-13): the mining scripts gained the snapshot
  cutoff and the label overrides, so `source_script_sha256` moved. The data
  files are byte-identical to the original build (verified by rebuilding from
  the source database; all three output hashes unchanged).
