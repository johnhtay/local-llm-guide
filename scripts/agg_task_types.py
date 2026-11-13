#!/usr/bin/env python3
"""Aggregate ALL opencode sessions (no work filter) into task-type totals.

Counterpart to mine_runtimes.py, which applies the work filter before printing
the chapter-09 session log. This one classifies every session so the guide can
say where the compute actually went (chapter 06, "Where the time actually went").

  think  = sum over assistant messages of (time.completed - time.created)
  tools  = sum over tool calls of (completed - ran, else created)
  active = think + tools

Filters mirror mine_runtimes.py: wall >= 2 min, active >= 30 s, warming
artifacts and excluded personal titles dropped.
Classification is rule-based on session titles; if no rule matches (or the
title is empty/generic), the first user message is classified with the same
rules before the session falls into the "Other" bucket.

Prints a markdown table (sessions, active total, share, average per session).
"""
import sqlite3
import os
import json
import hashlib
import re
from datetime import datetime

DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
MIN_WALL_MS = 120_000
MIN_ACTIVE_MS = 30_000

CATS = [
    ("Science & manuscripts",
     r"beast|mmm\b|manuscript|\.tex|references\.bib|figure|phyloplate|chronaeon|hyphaeon|rhizaeon"
     r"|episodic|mixed-effects|tdr\b|clock model|zika|sars-cov|tree sequence|relaxed_clock"
     r"|gamma distribution|preprint|bioinformatics|pubmed|coalescent|mtbd|scotti|asm 2026"
     r"|review outline|writing style|plate diagram|realprior|canary|anti-distillation|litsearch"
     r"|benchmark|phylodynamic|engram|phylo-aware|science|legend|layout fix|diagram|notation"
     r"|source tab|xml (search|zoom)|visualization prompt|veg\b|vibe-coded|code-stealing"
     r"|scholar|readings|paper summary|pdf (review|summary)|\.svg|arrowhead|governance"),
    ("Fleet, tooling & config",
     r"opencode|llama|\.bat|bat file|bat script|gguf|quant|context|dualgpu|gpu|vram|mcp|litellm"
     r"|proxy|keyring|bwrap|npm|git|server|strata|mmproj|drafter|mtp|dflash|ubatch|port\b|wsl"
     r"|memory|plugin|ponytail|ocgc|db\b|modelgen|forge|egpu|inference engine|footer|widget"
     r"|compaction|jinja|provider|api\b|cuda|nvfp4|ollama|tui|config|prefill|cmake|build crash"
     r"|openshell|cybtest|audit|untitled|webfetch|hf\b|huggingface|usb4|launch script|vision"),
    ("This Tutorial & documentation",
     r"tutorial|publishability|beginners guide|beginner|speed re-evaluation|voice and phrasing|metrics update"),
    ("Games & creative",
     r"game|three\.js|3d|horse|sprite|level-up|weapon|enemy|shotgun|projectile"
     r"|godot|snake|fps\b|creative|art\b|dendrogram|milankovitch|dog and cat|website planning"
     r"|webapp|animation|rendering|shooter|galloping|ui\b|chart|plot|pre-feature|flag check"
     r"|html implementation|dash key|ttk|health bar|obstacle|peeking|impact and explosion|rebalance"
     r"|sentinel|rocket\b"),
    ("Personal & admin",
     r"vulcan|ludwig|investment|econ-finance|household|bdf|fiscal|market data|ipo\b|roi\b"
     r"|heic|aldimobile|ldlc|windows|cv\b|resume|laptop|asus|tuf"
     r"|planning: research|shopping|constructs"),
]

OTHER = "Other (chats, Q&A, news)"


def is_warming_artifact(title, gen_tok):
    # v2 session-warming probes: untitled, a few hundred tokens across 13+ h open
    # time (10-22 cutover day); imported by mine_runtimes.py for the same filter.
    return not (title or "").strip() and gen_tok < 1000


# Sessions removed from the book entirely (personal entries the author asked to
# drop); every session-log miner applies this before classifying or tabulating.
# Titles are stored as SHA-256 prefixes only, so the repository carries no
# record of the excluded sessions themselves.
EXCLUDED_HASHES = frozenset({
    "b078e6684b421119",
    "6be93bca62cddd10",
    "ac5c524afc9c2e04",
    "6f15d96b4cc4b8f0",
    "34e7f68d4c95c528",
})


def is_excluded(title):
    t = (title or "").strip()
    if not t:
        return False
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16] in EXCLUDED_HASHES


def classify(title):
    t = (title or "untitled").lower()  # empty titles: v2-upgrade/proxy-diagnosis sessions
    for name, pat in CATS:
        if re.search(pat, t):
            return name
    return OTHER


def fmt_h(ms):
    ms = int(ms)
    return f"{ms // 3600000:d}h{(ms // 60000) % 60:02d}m"


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id,title,model,time_created,time_updated,tokens_output,tokens_reasoning"
        " FROM session_v2 ORDER BY time_created"
    ).fetchall()
    agg = {}
    n_total = 0
    for sid, title, model, tc, tu, tout, treason in rows:
        wall = tu - tc
        if wall < MIN_WALL_MS:
            continue
        if is_excluded(title):
            continue
        gen = tools = 0
        first_user = ""
        for typ, data in con.execute(
                "SELECT type,data FROM session_message WHERE session_id=? ORDER BY seq", (sid,)):
            if typ == "user" and not first_user:
                try:
                    first_user = (json.loads(data).get("text") or "")[:2000]
                except Exception:
                    pass
            if typ != "assistant":
                continue
            try:
                d = json.loads(data)
            except Exception:
                continue
            t = d.get("time") or {}
            if t.get("completed") is not None:
                gen += t["completed"] - (t.get("created") or t["completed"])
            for c in d.get("content") or []:
                if c.get("type") != "tool":
                    continue
                ct = c.get("time") or {}
                if ct.get("completed") is not None:
                    tools += ct["completed"] - (ct.get("ran") or ct.get("created") or ct["completed"])
        if gen + tools < MIN_ACTIVE_MS:
            continue
        if is_warming_artifact(title, (tout or 0) + (treason or 0)):
            continue
        cat = classify(title)
        if cat == OTHER:
            # generic titles ("Greeting", "Quick test"): sniff the first user message
            for name, pat in CATS:
                if re.search(pat, first_user.lower()):
                    cat = name
                    break
        a = agg.setdefault(cat, [0, 0])
        a[0] += 1
        a[1] += gen + tools
        n_total += 1
    total_active = sum(a[1] for a in agg.values())
    first = datetime.fromtimestamp(rows[0][3] / 1000).strftime("%Y-%m-%d")
    items = sorted(agg.items(), key=lambda kv: -kv[1][1])
    shares = [100.0 * act / total_active for _, (cnt, act) in items]
    cents = [round(s * 100) for s in shares]
    diff = 10000 - sum(cents)
    if diff:
        # largest-remainder: nudge the rows whose rounding error opposes the residual
        err = [(cents[i] - shares[i] * 100) * (1 if diff > 0 else -1) for i in range(len(cents))]
        for i in sorted(range(len(cents)), key=lambda i: -err[i])[:abs(diff)]:
            cents[i] += 1 if diff > 0 else -1
    print("| Task type | Sessions | Active total | Share | Avg per session |")
    print("|---|---|---|---|---|")
    for (name, (cnt, act)), c in zip(items, cents):
        print(f"| {name} | {cnt} | {fmt_h(act)} | {c / 100:.2f}% | "
              f"{fmt_h(act / cnt)} |")
    print(f"| **All sessions** | **{n_total}** | **{fmt_h(total_active)}** | 100.00% | "
          f"{fmt_h(total_active / n_total)} |")
    print(f"(first session {first}; active = think + tool time; wall-clock idle excluded)")


if __name__ == "__main__":
    main()
