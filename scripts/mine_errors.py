#!/usr/bin/env python3
"""Mine opencode's session DB for tool failures and who fixed them.

Counterpart to mine_runtimes.py (tempo) and agg_task_types.py (task types).
This one answers chapter 06's "pitfalls and debugging" question: how often do
the models' own errors arise, and are they self-corrected or does the human
step in? Printed per half: science work vs games/fun apps.

Failure events (chronological per session):
  real      bash/shell call completed with a non-zero exit code
  fumble    tool call failed outright: edit/read/grep mismatch, out-of-range
            read, malformed command line, schema misuse, memory-edit misses
  external  webfetch/websearch failures (bot-blocked 403s, 404s, timeouts)
  abort     tool run interrupted (user pressed escape)

Recovery: an event is "model-continued" if the model made any further tool
call before the next user message (it kept debugging in the same turn);
otherwise the turn ended on the failure.

Human step-in: a session counts once if, after the first failure, one of the
user's messages matches failure-report markers ("still", "again", "broken",
"didn't", "crashes", "hangs", "revert", ...). Rule-based, so approximate: it
catches both "your fix didn't work" and "what you built is broken in play".

Categories come from agg_task_types (session titles, first message fallback).
"""
import sqlite3
import os
import json
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agg_task_types import (CATS, OTHER, classify, MIN_WALL_MS, MIN_ACTIVE_MS,
                            is_excluded, SNAPSHOT_CUTOFF_MS)

DB = os.path.expanduser("~/.local/share/opencode/opencode.db")

FUMBLE_TOOLS = {"edit", "read", "grep", "glob", "write", "list", "task",
                "multiedit", "patch", "memory_replace", "memory_set",
                "memory_get", "todowrite", "question", "skill"}
EXTERNAL_TOOLS = {"webfetch", "websearch"}
BASH_TOOLS = {"bash", "shell"}
FAIL_KINDS = ("real", "fumble", "external", "abort")
HALVES = ("Science & manuscripts", "Games & creative")

INTERVEN = re.compile(
    r"\b(still|again|didn'?t|doesn'?t|not work|won'?t|broken|breaks|same error"
    r"|same issue|persist|nope|revert|undo|you broke|it fails?|that fails?"
    r"|crashes?|hangs?|froze)\b", re.I)


def kind_of(name, st):
    """Classify one tool part: (failure kind or 'ok', retry_ref).

    retry_ref identifies the operation for same-operation retry matching:
    the file path for file tools, the tool name otherwise."""
    status = st.get("status")
    if status == "error":
        msg = st.get("error") or ""
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        if '"aborted"' in msg[:30]:
            kind = "abort"
        elif name in EXTERNAL_TOOLS:
            kind = "external"
        else:
            # edit/read/grep mismatches AND malformed command lines are fumbles
            kind = "fumble"
    elif status == "completed" and name in BASH_TOOLS:
        if (st.get("metadata") or {}).get("exit") not in (0, None):
            kind = "real"
        else:
            kind = "ok"
    elif status == "completed":
        kind = "ok"
    else:
        return None, None
    inp = st.get("input") or {}
    ref = inp.get("filePath") if name in FILE_TOOLS else (inp.get("url") if name in EXTERNAL_TOOLS else None)
    return kind, (name, ref)


FILE_TOOLS = {"edit", "read", "write", "multiedit", "patch", "glob", "list"}


def timeline_of(con, sid):
    """Chronological [(kind, name_ref_or_None, user_text_or_None)] for one
    session; tool parts appear as their failure kind or 'ok' (a successful
    call). Events after the snapshot cutoff are excluded, matching the
    published data files."""
    out = []
    for typ, data, msg_created in con.execute(
            "SELECT type,data,time_created FROM session_message"
            " WHERE session_id=? ORDER BY seq", (sid,)):
        if typ == "user":
            if msg_created >= SNAPSHOT_CUTOFF_MS:
                continue
            try:
                out.append(("user", None, (json.loads(data).get("text") or "").strip()))
            except Exception:
                out.append(("user", None, ""))
        elif typ == "assistant":
            try:
                d = json.loads(data)
            except Exception:
                continue
            for c in d.get("content") or []:
                if not (isinstance(c, dict) and c.get("type") == "tool"):
                    continue
                ct = c.get("time") or {}
                comp = ct.get("completed")
                if comp is None or comp > SNAPSHOT_CUTOFF_MS \
                        or (ct.get("created") or msg_created) >= SNAPSHOT_CUTOFF_MS:
                    continue
                k, ref = kind_of(c.get("name") or "?", c.get("state") or {})
                if k:
                    out.append((k, ref, None))
    return out


def retried_in_turn(timeline, i):
    """True if the same operation is attempted again before the next user
    message: same file for file tools, same tool otherwise."""
    kind, (name, ref), _ = timeline[i]
    j = i + 1
    while j < len(timeline) and timeline[j][0] != "user":
        k, ref2, _ = timeline[j]
        if k in FAIL_KINDS + ("ok",) and ref2:
            n2, r2 = ref2
            if n2 == name and (name not in FILE_TOOLS or r2 == ref):
                return True
        j += 1
    return False


def cat_of(con, sid, title):
    cat = classify(title)
    if cat == OTHER:
        for typ, data in con.execute(
                "SELECT type,data FROM session_message WHERE session_id=? "
                "AND type='user' ORDER BY seq LIMIT 1", (sid,)):
            try:
                first = (json.loads(data).get("text") or "")[:2000].lower()
            except Exception:
                first = ""
            for name, pat in CATS:
                if re.search(pat, first):
                    return name
    return cat


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id,title,time_created,time_updated FROM session_v2"
        " WHERE time_created < ? ORDER BY time_created",
        (SNAPSHOT_CUTOFF_MS,)).fetchall()
    agg = {h: {"sessions": 0, "err_sessions": 0, "kinds": {}, "retried": {},
               "manual": 0} for h in HALVES}
    for sid, title, tc, tu in rows:
        cat = cat_of(con, sid, title)
        if cat not in agg:
            continue
        timeline = timeline_of(con, sid)
        # same filters as agg_task_types: wall >= 2 min, active (think+tools) >= 30 s
        wall = min(tu, SNAPSHOT_CUTOFF_MS) - tc
        if wall < MIN_WALL_MS:
            continue
        if is_excluded(title):
            continue
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
        agg[cat]["sessions"] += 1
        err_idx = [i for i, (k, _, _) in enumerate(timeline) if k in FAIL_KINDS]
        if not err_idx:
            continue
        agg[cat]["err_sessions"] += 1
        for i in err_idx:
            kind = timeline[i][0]
            agg[cat]["kinds"][kind] = agg[cat]["kinds"].get(kind, 0) + 1
            if retried_in_turn(timeline, i):
                agg[cat]["retried"][kind] = agg[cat]["retried"].get(kind, 0) + 1
        for i, (k, _, txt) in enumerate(timeline):
            if k == "user" and i > err_idx[0] and INTERVEN.search(txt or ""):
                agg[cat]["manual"] += 1
                break

    print("| Metric | Science & manuscripts | Games & creative |")
    print("|---|---|---|")
    s, g = (agg[h] for h in HALVES)
    def total(a):
        return sum(a["kinds"].values())
    def retried(a):
        return sum(a["retried"].values())
    print(f"| Sessions in the log | {s['sessions']} | {g['sessions']} |")
    print(f"| Sessions with at least one failure | {s['err_sessions']} "
          f"({100 * s['err_sessions'] / max(s['sessions'], 1):.0f}%) | {g['err_sessions']} "
          f"({100 * g['err_sessions'] / max(g['sessions'], 1):.0f}%) |")
    print(f"| Failure events | {total(s)} | {total(g)} |")
    for kind, label in (("real", "command failed (non-zero exit)"),
                        ("fumble", "agent fumble (mis-called tool)"),
                        ("external", "external (fetch blocked, 404, timeout)"),
                        ("abort", "interrupted (escape)")):
        print(f"| - {label} | {s['kinds'].get(kind, 0)} | {g['kinds'].get(kind, 0)} |")
    print(f"| Same operation retried before yielding | {100*retried(s)/total(s):.0f}% | "
          f"{100*retried(g)/total(g):.0f}% |")
    print(f"| Handed back without a retry | {100*(total(s)-retried(s))/total(s):.0f}% | "
          f"{100*(total(g)-retried(g))/total(g):.0f}% |")
    print(f"| Sessions needing a correction from me | "
          f"{s['manual']} ({100*s['manual']/s['sessions']:.0f}% of all) | "
          f"{g['manual']} ({100*g['manual']/g['sessions']:.0f}% of all) |")


if __name__ == "__main__":
    main()
