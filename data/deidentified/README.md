# Deidentified OpenCode session derivative

## Status and scope

This is a **deidentified, content-free release candidate, not an anonymous data set**. It requires a human disclosure review before public upload.

- Cutoff: November 10, 2026 at 20:28 Coordinated Universal Time (UTC), applied to individual messages and tool completions.
- Included records: 368 sessions, 290 work sessions and 37,964 tool events.
- Source access: a single read-only database transaction. The source database and mining scripts were not modified.
- Validation: source and derivative SQLite integrity checks passed; identifiers are unique; event counts match session denominators; automated free-text and path checks passed.

The earlier draft's 367 sessions and 289 work sessions came from a run several minutes earlier. The present derivative and `manuscript_auditable.md` deliberately use one coherent snapshot instead.

## Files

- `sessions.csv`: one row per eligible session.
- `tool_events.csv`: one content-free row per eligible tool call.
- `deidentified_opencode.db`: the same two tables in SQLite, plus a metadata table and an event-session index.
- `manifest.json`: cutoff, counts, tier rates, privacy checks, source-script hashes and output hashes.
- `../scripts/build_deidentified.py`: the build script.

Comma-separated values (CSV) files open in standard spreadsheet and statistical software. Use the SQLite file for reproducible queries without spreadsheet type conversion.

## What was removed

No prompts, responses, session titles, paths, commands, web addresses, model identifiers, original database identifiers or exact event timestamps are present. No free-text scientific content is present. Session identifiers are reassigned sequentially, and operation identifiers preserve only retry equivalence within a session.

The derivative supports recomputation of aggregate session and failure summaries. It does not support reconstruction of the original text-based task classifications, inspection of scientific claims or independent evaluation of the correction-marker language.

## `sessions.csv` fields

| Field | Meaning |
|---|---|
| `session_key` | Sequential pseudonym, S0001 to S0368, assigned in creation order. |
| `month` | UTC creation month, YYYY-MM. Exact creation dates are omitted. |
| `access_tier` | `institutional`, `public_cloud`, `public_free` or `local`. The manuscript and Fig 2 combine `public_free` with `public_cloud`. |
| `task_group` | One of six broad categories produced by the guide's rule-based classifier. |
| `is_work` | 1 for a work session and 0 for a home/non-work session under the guide's existing rule. |
| `wall_seconds` | Elapsed session time at the cutoff, capped at the cutoff and rounded to seconds. |
| `think_seconds` | Sum of assistant-message completion windows. These windows include tool execution time. |
| `tool_seconds` | Sum of tool execution windows. |
| `active_seconds` | `think_seconds + tool_seconds`. This is an upper bound because tool time is also inside assistant windows. |
| `user_messages` | Number of user messages before the cutoff. |
| `assistant_messages` | Number of assistant messages completed before the cutoff. |
| `tool_calls` | Number of classified tool events, the failure-rate denominator. |
| `input_tokens` | Uncached prompt tokens for assistant messages completed before the cutoff. |
| `cache_read_tokens` | Cached prompt tokens read before the cutoff. |
| `cache_write_tokens` | Prompt tokens written to cache before the cutoff. |
| `output_tokens` | Visible output tokens before the cutoff. |
| `reasoning_tokens` | Reasoning tokens before the cutoff. |
| `failure_events` | Number of command failures, tool errors, external blocks and user interruptions. |
| `retried_failures` | Failure events for which the same operation was attempted again before the next user message. |
| `human_correction` | 1 if the existing rule-based language heuristic detected a correction after the first failure. This is approximate, not manually adjudicated ground truth. |
| `failure_rate_universe` | 1 when the session has at least one tool call and therefore enters the tier-rate denominator. |

## `tool_events.csv` fields

| Field | Meaning |
|---|---|
| `event_key` | Sequential pseudonym, E000001 upward. |
| `session_key` | Link to `sessions.csv`. |
| `turn_index` | Number of user messages observed up to this event within the session. |
| `call_index` | Chronological tool-call index within the session. |
| `tool_group` | `shell`, `file`, `web`, `memory` or `other`. Exact tool names are not required for the reported rates. |
| `operation_group` | Session-local pseudonym for the operation identity used in retry matching. Paths and web addresses are never retained. |
| `outcome` | `ok`, `command_failure`, `tool_error`, `external_block` or `user_abort`. |
| `duration_seconds` | Tool execution duration, rounded to milliseconds. |
| `retried_same_turn` | 1 or 0 for failure events; blank for non-failures. |

`command_failure` means a completed shell command with a nonzero exit status. It is an operational proxy and can include expected control flow. `tool_error` means a failed tool call attributed to the model under the existing taxonomy. `external_block` covers web-fetch and web-search errors such as bot blocks, missing pages and timeouts. `user_abort` records an interrupted tool run.

## Rebuild

Use a new output directory. The script refuses to overwrite an existing directory.

```bash
python3 ../scripts/build_deidentified.py \
  --db /path/to/opencode.db \
  --scripts-dir /path/to/local-llms/scripts \
  --cutoff 2026-11-10T20:28:00Z \
  --output-dir /path/to/new-output
```

The mining directory must contain `agg_task_types.py`, `mine_errors.py` and `mine_runtimes.py` at the versions identified by hashes in `manifest.json`.

## Disclosure review before publication

1. Check whether month, durations, token totals and event sequences could identify a particular session when combined with public information.
2. Pay particular attention to small strata, including the two public free-tier sessions.
3. Consider rounding or suppressing fields not needed for a given release. Do not silently alter the snapshot used by the manuscript.
4. Confirm that `personal_admin`, `human_correction` and operation groupings carry no disclosure risk in context.
5. Record the manual decision and any additional minimization in a dated release note.

## Glossary

- **CSV:** Comma-separated values, a plain-text tabular format.
- **SQLite:** A serverless database system stored in a single local file.
- **UTC:** Coordinated Universal Time, the time standard used for the cutoff.
