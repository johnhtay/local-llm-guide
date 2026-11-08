#!/usr/bin/env python3
"""Mine opencode's session database for real-world runtime metrics.

Replicates the runtime-footer plugin's math:
  think  = sum over assistant messages of (time.completed - time.created)
           (the recorded window stays open until the message's last tool call
           finishes, so it includes tool execution time; true in v1 and v2)
  tools  = sum over tool calls of (completed - ran, else created)
           (v2 stamps the real execution start; v1 started the span when the
           model finished emitting the call)
  active = think + tools            wall = time_updated - time_created
           (tool time sits inside the think windows, so active double-counts
           it; read it as an upper bound on work time)
  tok/s  = (tokens_output + tokens_reasoning) / think seconds (prefill and
           tool time included)
  Split  = the served table carries Gen tok (tokens_output +
           tokens_reasoning) and then Reason tok (tokens_reasoning) and Out
           tok (tokens_output), each split cell with its share of the
           session's tokens in parentheses, as the provider's usage ledger
           reports them: the lab proxy and some Ollama Cloud models split
           reasoning out, llama-server does not. The local table therefore
           carries a single Gen tok column: the thinking is in the total,
           just not separated. A zero Reason tok in a cloud row means not
           measured, not no thinking. Reason + Out = Gen tok, the total that
           ~tok/s and the averages use
  Span   = median (time.streamed - time.created) per assistant message: the
           generation span of the median model call, request to its last
           streamed token (prefill, decode, provider latency). NOT time to
           first token: v2 stamps streamed when the stream ends, not when
           it starts. Checked in the database: text-only messages carry
           hundreds of tokens into a near-zero window after the stamp, and
           tokens over span lands at the decode speeds the fleets actually
           measure (median 47 tok/s local, 150 served). Span stamps exist
           only from the OpenCode v2 switch, 2026-10-22

Prints five markdown blocks separated by <!--SERVED-->, <!--HOME-LOCAL-->,
<!--HOME-SERVED--> and <!--AVERAGES--> (spliced into the chapter files by
scripts/splice_tables.py), plus a stdout-only <!--DERIVED--> block of
aggregates (span-derived rates, reasoning shares, tool shares) that the
chapter prose quotes.
  local    = work sessions on the user's hardware (llama.cpp dualGPU, Strata)
  served   = work sessions remote (litellm Pasteur proxy, Ollama Cloud, OpenCode
             free tier, Anthropic direct)
  home-*   = the same two tables for the sessions the work filter removes
             (games, creative builds, personal tasks, chats): same columns,
             same wall/active/warming bar, so work + home = the whole log
  averages = tier medians and token-weighted means, split by OpenCode era
             (v1 before the 2026-10-22 switch, v2 after) because the two eras
             are not directly comparable; the lab-proxy medium model changed
             again on 2026-10-29 (GLM 5.3 Flash NVFP4), so its v2 numbers also
             split at that date. The Tool-corrected column divides tokens by
             (think - tools), the share of the think window that was actually
             generation: an upper bound on decode speed, since prefill stays in.
             Averages cover work sessions only; home sessions never enter them.

A "Tool share" column (tool time as a share of the think window) accompanies
every row, and ROW_MARKS adds per-row explanation marks for the rows whose
slowness the share alone does not explain (see the legend in 09-runtimes.md).

Note: every Ollama-labelled session in this log was served by Ollama Cloud, not
a local Ollama install; the "(ollama)" provider label therefore maps to cloud.

Work filter: capability testing (games, creative builds) and personal tasks
(household finance, shopping, device admin, third-party CV reviews) are excluded
from the work tables; they are not discarded, they reappear as the home tables.
"""
import sqlite3
import os
import sys
import json
import re
import statistics
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agg_task_types import is_excluded, is_warming_artifact

DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
MIN_WALL_MS = 120_000
MIN_ACTIVE_MS = 30_000
SPAN_COVERAGE = 0.8  # min fraction of assistant msgs with a stream-end stamp to report Span med
# Era boundaries (UTC). v2 cutover: the 10-22 upgrade itself; sessions created
# before it ran on v1. Medium swap: litellm/medium became GLM 5.3 Flash NVFP4.
V2_CUTOVER = datetime(2026, 10, 22, tzinfo=timezone.utc)
MEDIUM_SWAP = datetime(2026, 10, 29, tzinfo=timezone.utc)

LABEL_OVERRIDES = {
    # This guide's own build session, displayed with the repo joke John asked for.
    "Local LLM setup tutorial":
        "Local LLM setup tutorial (for this very Gitlab repo :) )",
    # Home-log rows: a 31-char filename and CJK glyphs that overflow the Task
    # column or do not render in the PDF font (DejaVu Serif has no CJK).
    "Resume review: Yang_Ryan_Huang_Resume_2026.pdf":
        "Resume review (Yang CV)",
    "CSV ROI calculation with salary\u533a\u5206":
        "CSV ROI calculation with salary groups",
}
# Rows wrapped in <mark> per cell: GitLab renders a coloured highlight in both
# light and dark mode; pandoc keeps the text (highlight becomes plain) in the PDF.
# The highlighted rows are all sessions spent building this guide; the overrides
# above are plain shortenings and are not highlighted.
HIGHLIGHT = frozenset({
    "Local LLM setup tutorial (for this very Gitlab repo :) )",
    "09 local speed re-evaluation",
    "Writing voice and phrasing corrections",
})

NON_WORK = re.compile(
    r"vulcan|ludwig|\bVUL\b|investment|econ-finance|BdF|household asset|vignette"
    r"|fiscal|market data|IPO\b|ROI\b|heic|aldimobile|LDLC"
    r"|windows 11|\bCV\b|subah|riaz|resume review|resume:"
    r"|horse|weapon|enemy|shooter|shotgun|projectile|\bfps\b|rocket\b"
    r"|godot|snake|modelgen|three\.js|game\b|milankovitch|creative|free will"
    r"|dog and cat|map settings|html implementation|level-up"
    r"|rendering and performance|pre-feature|mobile bugs", re.I)

LOCAL_PIDS = {"strata-local"}

# Extra explanation marks appended to the ~tok/s cell (legend in 09-runtimes.md).
# Tool-dominated rows are not marked here: the Tool share column shows that share
# for every row. These two are the cases the share alone does not explain.
ROW_MARKS = {
    # Spans the 2026-11-02 sage restart: pre-restart the 4080 sat pinned at P4
    # (~435 MHz) while the eGPU boosted, and ~9 GB of context checkpoints drove
    # burst stalls down to 2-17 tok/s (decode ~29 tok/s at 150k+ depth on that
    # boot, ~68 tok/s after the restart).
    ("11-02", "PhyloPlate five-feature implementation"): "\u2021",
    # Prefill-dominated: 171k-token context, every tool result re-prefilled,
    # background compaction queued on the single slot.
    ("11-04", "Diagram view intelligent XML zoom"): "\u00a7",
}


def is_local(pid):
    if "local" in pid or "dualGPU" in pid:
        return True
    return pid in LOCAL_PIDS


def short_model(m):
    if not m:
        return "?"
    try:
        j = json.loads(m)
        pid = j.get("providerID", "?")
        mid = j.get("id", "?").split(":")[0].replace(":cloud", "")
        if pid == "litellm":
            return mid + " (served)"
        if "dualGPU" in pid or "local" in pid:
            return mid + " (local)"
        if pid == "ollama":
            return mid + " (ollama-cloud)"
        if pid == "ollama-cloud":
            return mid + " (ollama-cloud)"
        if pid == "opencode":
            return mid + " (free tier)"
        return f"{mid} ({pid})"
    except Exception:
        return "?"


def fmt_ms(ms):
    s = int(ms // 1000)
    if s >= 3600:
        return f"{s // 3600}h{s % 3600 // 60:02d}m{s % 60:02d}s"
    return f"{s // 60}m{s % 60:02d}s"


def fmt_sec(ms):
    s = ms / 1000
    if s >= 60:
        return f"{int(s // 60)}m{int(s % 60):02d}s"
    return f"{s:.1f}s"


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT id, title, model, time_created, time_updated,"
        " tokens_output, tokens_reasoning FROM session_v2 ORDER BY time_updated DESC"
    ).fetchall()
    local, served, stats = [], [], []
    home_local, home_served = [], []
    ledger = {}  # served work sessions: model -> [gen_tok, reasoning_tok]
    for sid, title, model, tc, tu, tout, treason in rows:
        if tu - tc < MIN_WALL_MS:
            continue
        gen = tools = 0
        prompts = ntool = 0
        spans = []
        total_msgs = 0
        streamed_msgs = 0
        for typ, data in con.execute(
                "SELECT type, data FROM session_message WHERE session_id=?", (sid,)):
            if typ == "user":
                prompts += 1
                continue
            if typ != "assistant":
                continue
            total_msgs += 1
            try:
                d = json.loads(data)
            except Exception:
                continue
            t = d.get("time") or {}
            if t.get("streamed") is not None and t.get("created") is not None:
                spans.append(t["streamed"] - t["created"])
                streamed_msgs += 1
            if t.get("completed") is not None:
                gen += t["completed"] - (t.get("created") or t["completed"])
            for c in d.get("content") or []:
                if c.get("type") != "tool":
                    continue
                ntool += 1
                ct = c.get("time") or {}
                if ct.get("completed") is not None:
                    tools += ct["completed"] - (ct.get("ran") or ct.get("created") or ct["completed"])
        if gen + tools < MIN_ACTIVE_MS:
            continue
        gen_tok = (tout or 0) + (treason or 0)
        if is_warming_artifact(title, gen_tok):
            continue
        if is_excluded(title):
            continue
        tps = gen_tok / (gen / 1000) if gen > 0 else 0.0
        date = datetime.fromtimestamp(tc / 1000).strftime("%m-%d")
        task = ((title or "").strip().replace("|", "/").replace("\u2014", "-") or "untitled")
        is_home = bool(NON_WORK.search(task))
        pid = json.loads(model).get("providerID", "") if model else ""
        tier = ("local" if is_local(pid) else
                "served" if pid == "litellm" else
                "ollama" if pid in ("ollama", "ollama-cloud") else "free")
        era = "v2" if tc >= V2_CUTOVER.timestamp() * 1000 else "v1"
        if not is_home:
            stats.append((era, tc, tier, gen, tools, gen_tok,
                          sum(spans), treason or 0, tout or 0))
        eng = short_model(model)
        if not is_home and tier == "served":
            mname = eng.split(" (")[0]
            ent = ledger.setdefault(mname, [0, 0])
            ent[0] += gen_tok
            ent[1] += treason or 0
        span_med = (statistics.median(spans) if spans
                    and streamed_msgs / max(total_msgs, 1) >= SPAN_COVERAGE
                    else None)
        span_str = fmt_sec(span_med) if span_med is not None else "n/a"
        task = LABEL_OVERRIDES.get(task, task)
        share = f"{tools / gen * 100:.0f}%" if gen else "0%"
        marks = ROW_MARKS.get((date, task), "")
        pct = max(gen_tok, 1)
        head = [date, eng, task, prompts, ntool, fmt_ms(gen), fmt_ms(tools),
                share, fmt_ms(gen + tools), span_str]
        tok = [f"{gen_tok:,}"]
        if tier != "local":
            tok += [f"{treason or 0:,} ({(treason or 0) / pct * 100:.0f}%)",
                    f"{tout or 0:,} ({(tout or 0) / pct * 100:.0f}%)"]
        cells = head + tok + [f"{tps:.0f}{marks}"]
        if task in HIGHLIGHT:
            cells = [f"<mark>{c}</mark>" for c in cells]
        row = "| " + " | ".join(str(c) for c in cells) + " |"
        if is_home:
            (home_local if tier == "local" else home_served).append(row)
        elif tier == "local":
            local.append(row)
        else:
            served.append(row)

    print("| Date | Engine | Task | Prompts | Tool calls | Think | Tools | Tool share | Active | Span med | Gen tok | ~tok/s |")
    print("|------|---------|-----------|--------|----|----------|----------|-----|----------|------|--------|------|")
    for line in local:
        print(line)
    print("<!--SERVED-->")
    print("| Date | Engine | Task | Prompts | Tool calls | Think | Tools | Tool share | Active | Span med | Gen tok | Reason tok | Out tok | ~tok/s |")
    print("|-----------|------------------|-----------------------|-----------------|--------|----------------------|----------------------|-----------|----------------------|------------|--------------------|------------------|------------------|-------------|")
    for line in served:
        print(line)
    print("<!--HOME-LOCAL-->")
    print("| Date | Engine | Task | Prompts | Tool calls | Think | Tools | Tool share | Active | Span med | Gen tok | ~tok/s |")
    print("|------|---------|-----------|--------|----|----------|----------|-----|----------|------|--------|------|")
    for line in home_local:
        print(line)
    print("<!--HOME-SERVED-->")
    print("| Date | Engine | Task | Prompts | Tool calls | Think | Tools | Tool share | Active | Span med | Gen tok | Reason tok | Out tok | ~tok/s |")
    print("|-----------|------------------|--------------------------|-----------------|--------|----------------------|----------------------|-----------|----------------------|------------|--------------------|------------------|------------------|-------------|")
    for line in home_served:
        print(line)

    # Era-split averages: medians, token-weighted means, and a tool-corrected
    # mean (tokens / (think - tools)) that removes tool execution from the
    # think window. Rows with tools >= think (parallel tool overlap in some v1
    # sessions) are excluded from the corrected column.
    swap_ms = MEDIUM_SWAP.timestamp() * 1000
    tiers = {"local": "Local rig", "served": "Lab proxy (served)",
             "ollama": "Ollama Cloud", "free": "Free tier"}
    print("<!--AVERAGES-->")
    print("| Era | Tier | Sessions | Median ~tok/s | Token-weighted | Tool-corrected |")
    print("|---|---|---|---|---|---|")
    for era, label in (("v1", "v1 (pre 10-22)"), ("v2", "v2 (10-22 and later)")):
        for tkey in ("local", "served", "ollama", "free"):
            sel = [s for s in stats if s[0] == era and s[2] == tkey]
            if not sel:
                continue
            print(avg_row(label, tiers[tkey], sel))
    for label, pred in (("pre 10-29 medium swap", lambda s: s[1] < swap_ms),
                        ("10-29 and later", lambda s: s[1] >= swap_ms)):
        sel = [s for s in stats if s[2] == "served" and pred(s)]
        if sel:
            print(avg_row(label, tiers["served"], sel))

    # Derived aggregates for the prose (stdout only; never spliced into the md).
    print("<!--DERIVED-->")
    for era, tkey in (("v2", "served"), ("v2", "local")):
        sel = [s for s in stats if s[0] == era and s[2] == tkey]
        if sel and sum(s[3] for s in sel):
            share = sum(s[4] for s in sel) / sum(s[3] for s in sel) * 100
            print(f"tool-share {era} {tkey}: {share:.0f}%")
        sel = [s for s in stats if s[0] == era and s[2] == tkey and s[3] > s[4]]
        if sel and sum(s[6] for s in sel):
            span_rate = sum(s[5] for s in sel) / (sum(s[6] for s in sel) / 1000)
            corr = (sum(s[5] for s in sel) /
                    sum(s[3] - s[4] for s in sel) * 1000)
            print(f"span-rate {era} {tkey}: {span_rate:.1f} tok/s "
                  f"(corrected {corr:.1f})")
    for m, (tok, reas) in sorted(ledger.items()):
        if tok > 500000:
            print(f"reason-share {m}: {reas / tok * 100:.0f}% of {tok / 1e6:.1f}M tok")


def avg_row(era, tier, sel):
    tps = [s[5] / (s[3] / 1000) for s in sel if s[3] > 0]
    tot_tok = sum(s[5] for s in sel)
    tot_gen = sum(s[3] for s in sel)
    corr = [s for s in sel if s[3] > s[4]]
    corr_val = (sum(s[5] for s in corr) /
                sum(s[3] - s[4] for s in corr) * 1000) if corr else None
    cells = [era, tier, str(len(sel)), f"{statistics.median(tps):.1f}",
             f"{tot_tok / max(tot_gen, 1) * 1000:.1f}",
             f"{corr_val:.1f}" if corr_val is not None else "n/a"]
    return "| " + " | ".join(cells) + " |"


if __name__ == "__main__":
    main()
