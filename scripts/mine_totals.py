#!/usr/bin/env python3
"""Resource totals behind the README's closing paragraph.

Session set: exactly the rows the runtime tables in 09-runtimes.md show, i.e.
the same filters as scripts/mine_runtimes.py (wall/active minima, warming
artifacts, exclusions) over every session in opencode's database, work and
home tiers summed together. The README's closing paragraph quotes the repo
scope below and points at ch 12 for these whole-log totals.

Cost scenarios price every token of that session set at the lab proxy's two
tiers, using ch 12's per-token table (OpenRouter, November 2026, USD per
million tokens): GLM-5.3 ("big") $0.07 in / $1.40 out, GLM-5.3-Flash
("medium") $0.15 in / $0.50 out. Raw input tokens, no cache discounts, so the
figures are ceilings, same convention as ch 12's reroute table.

A second scope prints the repo's own bill: sessions whose opencode directory
is the tutorial repo itself. These are the same four sessions the task-type
classifier in agg_task_types.py buckets as "This Tutorial & documentation"
(the build session, the ch 09 speed re-evaluation, the wording pass, and the
pre-publication sensitive-data check). Those sessions ran on the proxy's own
medium/big tiers, so the counterfactual there is close to what actually
happened.

Stdout only: the README paragraph quotes these numbers by hand, so re-run and
re-check the prose after any data change (the log keeps growing; see the live
caveat in 09-runtimes.md).
"""
import json
import sqlite3
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mine_runtimes as mr  # noqa: E402
from agg_task_types import is_excluded, is_warming_artifact  # noqa: E402

GLM_BIG = (0.07, 1.40)    # input, output per million tokens (GLM-5.3, "big")
GLM_FLASH = (0.15, 0.50)  # GLM-5.3-Flash, "medium"

# Reroute vendors mirror ch12's per-token table (OpenRouter, Nov 2026); update
# both together. "served" rows price the served tier's volume, "ollama" rows
# the Ollama Cloud tier's volume.
REROUTE = [
    ("GPT-6 Astra", "served", (10.00, 50.00)),
    ("Claude Fable 5.1", "served", (10.00, 50.00)),
    ("Claude Opus 5.5", "served", (4.00, 20.00)),
    ("Claude Sonnet 5.5", "served", (2.00, 10.00)),
    ("Gemini 3.8 Flash", "served", (0.83, 4.12)),
    ("GLM-5.3 Flash (OpenRouter)", "served", (0.15, 0.50)),
    ("Ollama Cloud at Mistral Large 4 rates", "ollama", (0.70, 2.10)),
]


def cost(tin, tgen, price):
    pin, pout = price
    return tin / 1e6 * pin + tgen / 1e6 * pout


REPO_DIR = "local_llm_tutorial"


def main():
    con = sqlite3.connect(mr.DB)
    rows = con.execute(
        "SELECT id, title, model, time_created, time_updated, directory,"
        " tokens_input, tokens_output, tokens_reasoning, cost FROM session_v2"
        " ORDER BY time_updated DESC").fetchall()
    n = work = home = 0
    think = tools_ms = 0
    prompts = ntool = 0
    tin = tout = treason = 0
    api_tin = api_tgen = 0
    loc_tin = loc_tgen = 0
    db_cost = 0.0
    tiers = {}
    sessions = []
    for sid, title, model, tc, tu, sdir, s_in, s_out, s_rea, s_cost in rows:
        if tu - tc < mr.MIN_WALL_MS:
            continue
        gen_ms = tool_ms = 0
        npr = ntl = 0
        for typ, data in con.execute(
                "SELECT type, data FROM session_message WHERE session_id=?", (sid,)):
            if typ == "user":
                npr += 1
                continue
            if typ != "assistant":
                continue
            try:
                d = json.loads(data)
            except Exception:
                continue
            t = d.get("time") or {}
            if t.get("completed") is not None:
                gen_ms += t["completed"] - (t.get("created") or t["completed"])
            for c in d.get("content") or []:
                if c.get("type") != "tool":
                    continue
                ntl += 1
                ct = c.get("time") or {}
                if ct.get("completed") is not None:
                    tool_ms += ct["completed"] - (ct.get("ran") or ct.get("created")
                                                  or ct["completed"])
        if gen_ms + tool_ms < mr.MIN_ACTIVE_MS:
            continue
        gen_tok = (s_out or 0) + (s_rea or 0)
        if is_warming_artifact(title, gen_tok) or is_excluded(title):
            continue
        task = ((title or "").strip().replace("|", "/").replace("\u2014", "-")
                or "untitled")
        pid = json.loads(model).get("providerID", "") if model else ""
        tier = ("local" if mr.is_local(pid) else
                "served" if pid == "litellm" else
                "ollama" if pid in ("ollama", "ollama-cloud") else "free")
        is_home = bool(mr.NON_WORK.search(task))
        n += 1
        work += 0 if is_home else 1
        home += 1 if is_home else 0
        think += gen_ms
        tools_ms += tool_ms
        prompts += npr
        ntool += ntl
        tin += s_in or 0
        tout += s_out or 0
        treason += s_rea or 0
        db_cost += s_cost or 0
        t = tiers.setdefault(tier, [0, 0, 0, 0.0, 0, 0, 0, 0])
        t[0] += s_in or 0
        t[1] += s_out or 0
        t[2] += s_rea or 0
        t[3] += s_cost or 0
        t[4] += 1
        t[5] += 0 if is_home else 1
        if not is_home:
            t[6] += s_in or 0
            t[7] += gen_tok
        if tier == "local":
            loc_tin += s_in or 0
            loc_tgen += gen_tok
        else:
            api_tin += s_in or 0
            api_tgen += gen_tok
        mid = json.loads(model).get("id", "") if model else ""
        sessions.append((sdir or "", title, mid, s_in or 0, gen_tok,
                         s_out or 0, s_rea or 0, gen_ms, tool_ms, npr, ntl))

    gen = tout + treason
    dates = sorted(datetime.fromtimestamp(r[3] / 1000) for r in rows)
    print(f"span: {dates[0]:%Y-%m-%d} to {dates[-1]:%Y-%m-%d}")
    print(f"sessions: {n} total (work {work}, home {home})")
    print("ch12 volume-table basis (work sessions; Output = out + reasoning):")
    for tier, (a, b, r, c, na, nw, wi, wg) in sorted(tiers.items()):
        print(f"  {tier:7s} work-only: input {wi/1e6:,.0f}M, output {wg/1e6:.1f}M"
              f" ({nw} sessions) | all: input {a/1e6:,.0f}M, output "
              f"{(b + r)/1e6:.1f}M ({na} sessions)")
    print("reroute (ch12 table, work-only volumes):")
    for name, basis, price in REROUTE:
        wi, wg = tiers[basis][6], tiers[basis][7]
        print(f"  {name:40s} on {basis:6s}: input {wi/1e6:,.0f}M, "
              f"output {wg/1e6:.1f}M -> ${cost(wi, wg, price):,.0f}")
    print(f"time: think {think/3.6e6:.1f}h (tools {tools_ms/3.6e6:.1f}h, "
          f"pure generation {(think - tools_ms)/3.6e6:.1f}h)")
    print(f"prompts: {prompts:,}   tool calls: {ntool:,}")
    print(f"tokens: input {tin/1e9:.2f}B, generated {gen/1e6:.1f}M "
          f"(reasoning {treason/1e6:.1f}M, visible out {tout/1e6:.1f}M)")
    print(f"  api side (served+ollama+free): input {api_tin/1e9:.2f}B, "
          f"gen {api_tgen/1e6:.1f}M")
    print(f"  local rig:                     input {loc_tin/1e9:.2f}B, "
          f"gen {loc_tgen/1e6:.1f}M")
    print(f"cost at GLM-5.3 ('big') rates:      everything ${cost(tin, gen, GLM_BIG):,.0f}"
          f" | api side ${cost(api_tin, api_tgen, GLM_BIG):,.0f}"
          f" | local share ${cost(loc_tin, loc_tgen, GLM_BIG):,.0f}")
    print(f"cost at GLM-5.3-Flash ('medium'):   everything ${cost(tin, gen, GLM_FLASH):,.0f}"
          f" | api side ${cost(api_tin, api_tgen, GLM_FLASH):,.0f}"
          f" | local share ${cost(loc_tin, loc_tgen, GLM_FLASH):,.0f}")
    print("opencode's own cost ledger by tier:")
    for tier, (a, b, r, c, na, nw, wi, wg) in sorted(tiers.items()):
        if c:
            print(f"  {tier:7s} ${c:,.0f}")
    print(f"opencode's own per-model ledger (reference only): ${db_cost:,.0f}")

    print()
    print("repo scope: sessions run inside the tutorial repo's directory")
    repo = [s for s in sessions if REPO_DIR in s[0]]
    r_think = sum(s[7] for s in repo)
    r_tools = sum(s[8] for s in repo)
    r_prompts = sum(s[9] for s in repo)
    r_calls = sum(s[10] for s in repo)
    r_in = sum(s[3] for s in repo)
    r_gen = sum(s[4] for s in repo)
    r_out = sum(s[5] for s in repo)
    r_rea = sum(s[6] for s in repo)
    # each session priced at its own tier: medium -> Flash, big -> GLM-5.3
    r_cost = sum(cost(s[3], s[4], GLM_FLASH if s[2] == "medium" else GLM_BIG)
                 for s in repo)
    for s in repo:
        c = cost(s[3], s[4], GLM_FLASH if s[2] == "medium" else GLM_BIG)
        print(f"  {s[1][:44]:44s} {s[2]:6s} in {s[3]/1e6:7.1f}M "
              f"gen {s[4]/1e6:4.1f}M -> ${c:.3f}")
    print(f"sessions: {len(repo)}")
    print(f"time: think {r_think/3.6e6:.1f}h (tools {r_tools/3.6e6:.1f}h, "
          f"pure generation {(r_think - r_tools)/3.6e6:.1f}h)")
    print(f"prompts: {r_prompts:,}   tool calls: {r_calls:,}")
    print(f"tokens: input {r_in/1e6:.1f}M, generated {r_gen/1e6:.2f}M "
          f"(reasoning {r_rea/1e6:.2f}M, visible out {r_out/1e6:.2f}M)")
    print(f"cost, each session at its own tier:   ${r_cost:.3f}")
    print(f"cost, everything at GLM-5.3 'big':    ${cost(r_in, r_gen, GLM_BIG):.3f}")
    print(f"cost, everything at GLM-5.3-Flash:    ${cost(r_in, r_gen, GLM_FLASH):.3f}")


if __name__ == "__main__":
    main()
