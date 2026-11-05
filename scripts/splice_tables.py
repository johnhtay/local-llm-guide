#!/usr/bin/env python3
"""Regenerate the generated tables in chapters 09 and 10.

Runs the four mining scripts and splices their table blocks into the chapter
files at the placeholder tables. A table's position is found by header prefix
and occurrence number, so a chapter can carry several tables with the same
header (the four runtime tables in 09). Run from anywhere; paths are resolved
from this file's location.
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def run(script):
    out = subprocess.run([sys.executable, os.path.join(REPO, "scripts", script)],
                         capture_output=True, text=True, check=True)
    return out.stdout


def table_lines(text, start_marker):
    lines = text.splitlines()
    idx = next(i for i, l in enumerate(lines) if l.startswith(start_marker))
    block = []
    for l in lines[idx:]:
        if not l.startswith("|"):
            break
        block.append(l)
    return block


def splice(path, replacements):
    lines = open(path).read().splitlines()
    spans = []
    for prefix, nth, new in replacements:
        hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        assert len(hits) >= nth, (path, prefix, nth, hits)
        start = hits[nth - 1]
        end = start
        while end < len(lines) and lines[end].startswith("|"):
            end += 1
        spans.append((start, end, new))
    for start, end, new in sorted(spans, reverse=True):
        lines[start:end] = new
    open(path, "w").write("\n".join(lines) + "\n")
    return [(p, n, len(w)) for (p, n, w), (s, e, _t) in zip(replacements, spans)]


runtime = run("mine_runtimes.py")
tasks = run("agg_task_types.py")
fails = run("mine_failures_by_model.py")
errors = run("mine_errors.py")

local_part, rest = runtime.split("<!--SERVED-->", 1)
served_part, rest = rest.split("<!--HOME-LOCAL-->", 1)
hlocal_part, rest = rest.split("<!--HOME-SERVED-->", 1)
hserved_part, avg_part = rest.split("<!--AVERAGES-->", 1)

ch09 = [
    ("| Date | Engine", 1, table_lines(local_part, "| Date | Engine")),
    ("| Date | Engine", 2, table_lines(served_part, "| Date | Engine")),
    ("| Date | Engine", 3, table_lines(hlocal_part, "| Date | Engine")),
    ("| Date | Engine", 4, table_lines(hserved_part, "| Date | Engine")),
    ("| Era | Tier | Sessions |", 1,
     table_lines(avg_part, "| Era | Tier | Sessions |")),
    ("| Task type | Sessions |", 1,
     table_lines(tasks, "| Task type | Sessions |")),
]
ch10 = [
    ("| Metric | Science", 1, table_lines(errors, "| Metric | Science")),
    ("| Access tier | Sessions |", 1,
     table_lines(fails, "| Access tier | Sessions |")),
    ("| Model | Tier | Sessions |", 1,
     table_lines(fails, "| Model | Tier | Sessions |")),
]

for rel, reps in (("09-runtimes.md", ch09), ("10-pitfalls.md", ch10)):
    print(f"spliced {rel}:")
    for prefix, nth, size in splice(os.path.join(REPO, rel), reps):
        print(f"  {prefix!r} #{nth}: {size} lines")
