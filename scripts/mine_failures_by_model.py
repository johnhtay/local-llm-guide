#!/usr/bin/env python3
"""Failure rates by access tier and by model (chapter 09, pitfalls section).

Universe: every session with wall >= 2 min, active >= 30 s, at least one tool
call, and not a warming artifact (agg_task_types.is_warming_artifact). This is
wider than mine_errors.py's science/games halves: rates want every tool call,
not just the two halves.

Failure events reuse mine_errors.kind_of via timeline_of: real = completed
bash/shell with non-zero exit, fumble = tool-status error (edit/read/grep
mismatches, malformed commands), external = webfetch/websearch blocks,
abort = interrupted by the user.

Rate denominators are tool calls. Sessions that switched engines midway are
attributed to their final model, as in the session-log tables. Models with
fewer than MIN_MODEL_SESSIONS are summed into one "other" row.
"""
import sqlite3
import os
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agg_task_types import (DB, MIN_WALL_MS, MIN_ACTIVE_MS, is_excluded,
                            is_warming_artifact, SNAPSHOT_CUTOFF_MS)
from mine_errors import FAIL_KINDS, timeline_of

MIN_MODEL_SESSIONS = 4

TIERS = {
    "litellm": "Pasteur served",
    "ollama": "Ollama Cloud",
    "ollama-cloud": "Ollama Cloud",
    "opencode": "Free tier",
}


def tier_of(prov):
    return TIERS.get(prov, "Local rig" if "local" in prov else "Free tier")


def display(prov, mid):
    if prov == "litellm":
        return f"{mid} (served)"
    if prov.startswith("ollama"):
        return f"{mid.split(':')[0]} (ollama-cloud)"
    return mid


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id,title,model,time_created,time_updated,tokens_output,tokens_reasoning"
        " FROM session_v2 WHERE time_created < ? ORDER BY time_created",
        (SNAPSHOT_CUTOFF_MS,)).fetchall()
    agg_t = defaultdict(lambda: [0, 0, 0, 0, Counter()])
    agg_m = defaultdict(lambda: [0, 0, 0, 0, Counter()])
    for sid, title, model, tc, tu, tout, treason in rows:
        if min(tu, SNAPSHOT_CUTOFF_MS) - tc < MIN_WALL_MS:
            continue
        if is_warming_artifact(title, (tout or 0) + (treason or 0)):
            continue
        if is_excluded(title):
            continue
        try:
            m = json.loads(model)
            prov, mid = m.get("providerID", "?"), m.get("id", "?")
        except Exception:
            prov, mid = "?", "?"
        # Same minimum-active filter as the other miners (think + tool time
        # >= 30 s, frozen at the snapshot cutoff): sessions below it are not
        # in the published data files either.
        active = 0
        for typ, data, msg_created in con.execute(
                "SELECT type,data,time_created FROM session_message WHERE session_id=?", (sid,)):
            if typ != "assistant":
                continue
            try:
                d = json.loads(data)
            except Exception:
                continue
            t = d.get("time") or {}
            completed = t.get("completed")
            if completed is not None and completed <= SNAPSHOT_CUTOFF_MS:
                active += completed - (t.get("created") or completed)
            for c in d.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool":
                    ct = c.get("time") or {}
                    comp = ct.get("completed")
                    if comp is None or comp > SNAPSHOT_CUTOFF_MS \
                            or (ct.get("created") or msg_created) >= SNAPSHOT_CUTOFF_MS:
                        continue
                    active += comp - (ct.get("ran") or ct.get("created") or msg_created or comp)
        if active < MIN_ACTIVE_MS:
            continue
        timeline = timeline_of(con, sid)
        calls = sum(1 for k, _, _ in timeline if k != "user")
        fails = [k for k, _, _ in timeline if k in FAIL_KINDS]
        if calls == 0:
            continue  # chat-only session: no denominator to rate
        tk = tier_of(prov)
        mk = (display(prov, mid), tk)
        for agg, key in ((agg_t, tk), (agg_m, mk)):
            a = agg[key]
            a[0] += 1
            a[1] += calls
            a[2] += len(fails)
            a[3] += 1 if fails else 0
            for k in fails:
                a[4][k] += 1

    def row(name, tier, a):
        s, c, f, fs, kinds = a
        return (f"| {name} | {tier} | {s} | {c:,} | {100 * f / c:.1f} "
                f"| {100 * kinds['fumble'] / c:.1f} | {100 * fs / s:.0f}% |")

    print("| Model | Tier | Sessions | Tool calls | Fails /100 calls | Fumbles /100 calls | Sessions w/ failure |")
    print("|---|---|---|---|---|---|---|")
    items = sorted(agg_m.items(), key=lambda kv: -kv[1][1])
    rest = [a for k, a in items if a[0] < MIN_MODEL_SESSIONS]
    for (name, tier), a in items:
        if a[0] >= MIN_MODEL_SESSIONS:
            print(row(name, tier, a))
    if rest:
        merged = [sum(a[i] for a in rest) for i in range(4)]
        kinds = Counter()
        for a in rest:
            kinds += a[4]
        print(row("Other models (under 4 sessions each)", "mixed", merged + [kinds]))

    print()
    print("| Access tier | Sessions | Tool calls | Fails /100 calls | real | fumble | external | abort | Sessions w/ failure |")
    print("|---|---|---|---|---|---|---|---|---|")
    for t, a in sorted(agg_t.items(), key=lambda kv: -kv[1][1]):
        s, c, f, fs, kinds = a
        print(f"| {t} | {s} | {c:,} | {100 * f / c:.1f} | {kinds['real']} "
              f"| {kinds['fumble']} | {kinds['external']} | {kinds['abort']} "
              f"| {100 * fs / s:.0f}% |")


if __name__ == "__main__":
    main()
