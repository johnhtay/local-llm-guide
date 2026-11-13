#!/usr/bin/env python3
"""Build a content-free, deidentified snapshot of the OpenCode session log.

No prompt, response, title, path, command, URL, model ID or original database ID
is written. The output directory must not exist, which prevents overwriting.
"""
import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TASK_GROUPS = {
    "Science & manuscripts": "science_manuscripts",
    "Fleet, tooling & config": "fleet_tooling_config",
    "This Tutorial & documentation": "tutorial_documentation",
    "Games & creative": "games_creative",
    "Personal & admin": "personal_admin",
    "Other (chats, Q&A, news)": "other",
}
OUTCOMES = {"real": "command_failure", "fumble": "tool_error",
            "external": "external_block", "abort": "user_abort"}


def parse_cutoff(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Cutoff must include a timezone, for example Z")
    return int(dt.timestamp() * 1000)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--scripts-dir", type=Path, required=True,
                        help="Read-only directory containing the guide's mining scripts")
    parser.add_argument("--cutoff", required=True,
                        help="ISO timestamp; messages and tools completed after it are excluded")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"Refusing to use existing output directory: {args.output_dir}")
    cutoff = parse_cutoff(args.cutoff)
    sys.path.insert(0, str(args.scripts_dir.resolve()))
    import agg_task_types as ag
    import mine_errors as me
    import mine_runtimes as mr

    source_files = [args.scripts_dir / name for name in
                    ("agg_task_types.py", "mine_errors.py", "mine_runtimes.py")]
    con = sqlite3.connect(f"file:{args.db.resolve()}?mode=ro", uri=True)
    con.execute("BEGIN")
    integrity = con.execute("PRAGMA quick_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError("Source database failed quick_check")

    sessions, events = [], []
    category_counts = Counter()
    for sid, title, model, tc, tu in con.execute(
            "SELECT id,title,model,time_created,time_updated FROM session_v2 "
            "WHERE time_created < ? ORDER BY time_created", (cutoff,)):
        wall = min(tu, cutoff) - tc
        if wall < ag.MIN_WALL_MS or ag.is_excluded(title):
            continue
        think = tools = 0
        n_user = n_assistant = 0
        tokens = Counter()
        first_user = ""
        timeline = []
        raw_tools = []
        for typ, data, msg_created in con.execute(
                "SELECT type,data,time_created FROM session_message "
                "WHERE session_id=? ORDER BY seq", (sid,)):
            if typ == "user":
                if msg_created >= cutoff:
                    continue
                n_user += 1
                try:
                    text = (json.loads(data).get("text") or "").strip()
                except Exception:
                    text = ""
                if not first_user:
                    first_user = text[:2000].lower()
                timeline.append(("user", None, text))
                continue
            if typ != "assistant":
                continue
            try:
                d = json.loads(data)
            except Exception:
                continue
            t = d.get("time") or {}
            if t.get("completed") is not None and t["completed"] <= cutoff:
                n_assistant += 1
                think += t["completed"] - (t.get("created") or t["completed"])
                tok = d.get("tokens") or {}
                for key in ("input", "output", "reasoning"):
                    tokens[key] += tok.get(key) or 0
                cache = tok.get("cache") or {}
                tokens["cache_read"] += cache.get("read") or 0
                tokens["cache_write"] += cache.get("write") or 0
            for c in d.get("content") or []:
                if not isinstance(c, dict) or c.get("type") != "tool":
                    continue
                ct = c.get("time") or {}
                completed = ct.get("completed")
                created = ct.get("created") or msg_created
                if completed is None or completed > cutoff or created >= cutoff:
                    continue
                duration = completed - (ct.get("ran") or created)
                tools += duration
                name = c.get("name") or "?"
                state = c.get("state") or {}
                kind, ref = me.kind_of(name, state)
                if not kind:
                    continue
                timeline.append((kind, ref, None))
                raw_tools.append((name, ref, kind, duration))
        gen_tok = tokens["output"] + tokens["reasoning"]
        if think + tools < ag.MIN_ACTIVE_MS or ag.is_warming_artifact(title, gen_tok):
            continue

        category = ag.classify(title)
        if category == ag.OTHER:
            for name, pattern in ag.CATS:
                if re.search(pattern, first_user):
                    category = name
                    break
        try:
            provider = (json.loads(model) or {}).get("providerID", "")
        except Exception:
            provider = ""
        tier = ("local" if mr.is_local(provider) else
                "institutional" if provider == "litellm" else
                "public_cloud" if provider in ("ollama", "ollama-cloud") else "public_free")
        is_work = not bool(mr.NON_WORK.search((title or "").strip()))
        session_key = f"S{len(sessions) + 1:04d}"
        operation_ids = {}
        failure_indices = [i for i, row in enumerate(timeline) if row[0] in me.FAIL_KINDS]
        retried = sum(me.retried_in_turn(timeline, i) for i in failure_indices)
        correction = False
        if failure_indices:
            for i, (kind, _, text) in enumerate(timeline):
                if kind == "user" and i > failure_indices[0] and me.INTERVEN.search(text or ""):
                    correction = True
                    break
        call_index = 0
        for name, ref, kind, duration in raw_tools:
            call_index += 1
            # The operation identifier preserves retry equivalence without retaining paths or URLs.
            operation_key = (name, ref)
            if operation_key not in operation_ids:
                operation_ids[operation_key] = len(operation_ids) + 1
            if name in me.BASH_TOOLS:
                tool_group = "shell"
            elif name in me.FILE_TOOLS:
                tool_group = "file"
            elif name in me.EXTERNAL_TOOLS:
                tool_group = "web"
            elif name.startswith("memory_"):
                tool_group = "memory"
            else:
                tool_group = "other"
            turn_index = sum(1 for row in timeline[:call_index] if row[0] == "user")
            # Derive the turn from chronological position, including interleaved user messages.
            timeline_position = 0
            seen_calls = 0
            for j, row in enumerate(timeline):
                if row[0] != "user":
                    seen_calls += 1
                    if seen_calls == call_index:
                        timeline_position = j
                        break
            turn_index = sum(row[0] == "user" for row in timeline[:timeline_position + 1])
            is_failure = kind in me.FAIL_KINDS
            events.append({
                "event_key": f"E{len(events) + 1:06d}", "session_key": session_key,
                "turn_index": turn_index, "call_index": call_index,
                "tool_group": tool_group,
                "operation_group": f"op{operation_ids[operation_key]:04d}",
                "outcome": OUTCOMES.get(kind, "ok"),
                "duration_seconds": round(max(duration, 0) / 1000, 3),
                "retried_same_turn": (int(me.retried_in_turn(timeline, timeline_position))
                                      if is_failure else ""),
            })
        sessions.append({
            "session_key": session_key,
            "month": datetime.fromtimestamp(tc / 1000, timezone.utc).strftime("%Y-%m"),
            "access_tier": tier, "task_group": TASK_GROUPS[category],
            "is_work": int(is_work), "wall_seconds": round(wall / 1000),
            "think_seconds": round(think / 1000), "tool_seconds": round(tools / 1000),
            "active_seconds": round((think + tools) / 1000),
            "user_messages": n_user, "assistant_messages": n_assistant,
            "tool_calls": len(raw_tools), "input_tokens": tokens["input"],
            "cache_read_tokens": tokens["cache_read"],
            "cache_write_tokens": tokens["cache_write"],
            "output_tokens": tokens["output"], "reasoning_tokens": tokens["reasoning"],
            "failure_events": len(failure_indices), "retried_failures": retried,
            "human_correction": int(correction),
            "failure_rate_universe": int(bool(raw_tools)),
        })
        category_counts[category] += 1
    con.close()

    args.output_dir.mkdir(parents=True)
    for filename, rows in (("sessions.csv", sessions), ("tool_events.csv", events)):
        with (args.output_dir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    db_path = args.output_dir / "deidentified_opencode.db"
    out = sqlite3.connect(db_path)
    out.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
    out.executemany("INSERT INTO metadata VALUES (?,?)", [
        ("cutoff_utc", datetime.fromtimestamp(cutoff / 1000, timezone.utc).isoformat()),
        ("privacy_status", "deidentified_content_free_not_anonymous"),
        ("source_scripts", "agg_task_types.py;mine_errors.py;mine_runtimes.py"),
    ])
    for table, rows in (("sessions", sessions), ("tool_events", events)):
        columns = list(rows[0])
        defs = []
        for col in columns:
            val = rows[0][col]
            defs.append(f'"{col}" ' + ("INTEGER" if isinstance(val, int) else
                                      "REAL" if isinstance(val, float) else "TEXT"))
        out.execute(f'CREATE TABLE {table} ({",".join(defs)})')
        placeholders = ",".join("?" for _ in columns)
        out.executemany(f'INSERT INTO {table} VALUES ({placeholders})',
                        [[row[col] for col in columns] for row in rows])
    out.execute("CREATE INDEX idx_events_session ON tool_events(session_key)")
    out.commit()
    out.close()

    # Content and reproducibility checks operate on the released rows, not the source text.
    assert len({row["session_key"] for row in sessions}) == len(sessions)
    assert len({row["event_key"] for row in events}) == len(events)
    assert all(row["tool_calls"] == sum(e["session_key"] == row["session_key"] for e in events)
               for row in sessions)
    for rows in (sessions, events):
        for row in rows:
            for value in row.values():
                if isinstance(value, str):
                    assert len(value) <= 64 and not any(x in value for x in ("/", "\\", "@", "\n", "\r"))
    tier_rates = {}
    for tier in sorted({row["access_tier"] for row in sessions}):
        selected = [row for row in sessions if row["access_tier"] == tier and row["failure_rate_universe"]]
        calls = sum(row["tool_calls"] for row in selected)
        failures = sum(row["failure_events"] for row in selected)
        tier_rates[tier] = {"sessions": len(selected), "tool_calls": calls,
                            "failure_events": failures,
                            "failures_per_100_calls": round(100 * failures / calls, 3) if calls else None}
    manifest = {
        "cutoff_utc": datetime.fromtimestamp(cutoff / 1000, timezone.utc).isoformat(),
        "source_quick_check": integrity,
        "source_script_sha256": {p.name: sha256(p) for p in source_files},
        "sessions": len(sessions), "work_sessions": sum(s["is_work"] for s in sessions),
        "tool_events": len(events), "task_group_counts": dict(sorted(Counter(
            s["task_group"] for s in sessions).items())),
        "failure_rates_by_tier": tier_rates,
        "privacy": {
            "status": "deidentified_content_free_not_anonymous",
            "excluded": ["prompts", "responses", "titles", "paths", "commands", "URLs",
                         "model IDs", "original database IDs", "exact event timestamps"],
            "automated_content_checks": "passed",
            "manual_disclosure_review_required": True,
        },
        "output_sha256": {},
    }
    for name in ("sessions.csv", "tool_events.csv", "deidentified_opencode.db"):
        manifest["output_sha256"][name] = sha256(args.output_dir / name)
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in
                      ("cutoff_utc", "sessions", "work_sessions", "tool_events",
                       "task_group_counts", "failure_rates_by_tier")}, indent=2))
    print("Privacy checks: passed; manual disclosure review still required")


if __name__ == "__main__":
    main()
