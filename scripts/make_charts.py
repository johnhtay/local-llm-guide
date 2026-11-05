#!/usr/bin/env python3
"""Generate the SVG charts used across the guide: 10, 11, 02, 08 and beginner 01/02.

Data source: Artificial Analysis Intelligence Index v5.0.1, retrieved 2026-11-04
from artificialanalysis.ai/leaderboards/models and the v5 announcement article.
Prices are USD per Intelligence Index task as published by Artificial Analysis.
Local-fleet rows are marked by us, not by Artificial Analysis.

Run: python3 scripts/make_charts.py   (writes charts/*.svg + charts/*.png at the repo root, from any working directory)
"""
import os

# Output anchors to the repo root (one level above this script), not the cwd,
# so the charts land in charts/ no matter where the script is invoked from.
OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "charts"))

try:
    import cairosvg
except ImportError:
    cairosvg = None

# (label, score, category)  categories: closed | open | open-unreleased | fleet
AA_INDEX = [
    ("Gemini 4 Carbon (high)", 60, "closed"),
    ("Claude Opus 5.5 (max)", 59, "closed"),
    ("GPT-6 Astra (max)", 57, "closed"),
    ("GPT-6.1 Sol (max)", 55, "closed"),
    ("Claude Sonnet 5.5 (max)", 55, "closed"),
    ("GPT-6.1 Terra (max)", 51, "closed"),
    ("Kimi K3.1 Pro", 46, "open"),
    ("Claude Haiku 5.5 (max)", 36, "closed"),
    ("Qwen3.8 Max (0902)", 34, "open-unreleased"),
    ("DeepSeek V4.1 Flash 1017 (max)", 33, "open"),
    ("GLM-5.3 (max, Pasteur IA 'big')", 32, "pasteur"),
    ("MiMo-V2.6-Pro", 30, "open"),
    ("Ling 3.1 Flash 1019", 30, "open"),
    ("MiniMax-M3.1-Flash", 29, "open"),
    ("DeepSeek V4.1 Flash 1017 (high)", 29, "open"),
    ("GLM-5.3-Flash (Pasteur IA 'medium')", 28, "pasteur"),
    ("MiMo-V2.6-Flash", 27, "open"),
    ("Mistral Large 4 (high)", 26, "open"),
    ("Nanbeige4.3-33B (ran on the rig)", 20, "fleet"),
    ("Qwen3.8 27B (xhigh, stock)", 20, "fleet"),
]

# (label, cost per task USD, category)
COST_PER_TASK = [
    ("Claude Fable 5.1 (max)", 12.99, "closed"),
    ("Claude Opus 5.5 (max)", 10.04, "closed"),
    ("Grok 4.7 (xhigh)", 7.77, "closed"),
    ("Gemini 4 Carbon (high)", 7.76, "closed"),
    ("GPT-6 Astra (max)", 6.24, "closed"),
    ("GLM-5.3 (max, Pasteur IA 'big')", 5.01, "pasteur"),
    ("Kimi K3.1 Pro", 3.68, "open"),
    ("Qwen3.8 27B (xhigh, stock)", 3.53, "fleet"),
    ("Mistral Large 4 (high)", 2.06, "open"),
    ("GPT-6.1 Sol (max)", 1.27, "closed"),
    ("GPT-6.1 Terra (max)", 0.96, "closed"),
    ("DeepSeek V4.1 Flash 1017 (max)", 0.60, "open"),
    ("GLM-5.3-Flash (Pasteur IA 'medium')", 0.58, "pasteur"),
    ("MiniMax-M3.1-Flash", 0.49, "open"),
    ("MiMo-V2.6-Pro", 0.26, "open"),
    ("Local rig (this guide)", 0.00, "fleet"),
]

COLORS = {
    "closed": "#3572a5",
    "open": "#2ea043",
    "open-unreleased": "#9e9e9e",
    "fleet": "#d29922",
    "pasteur": "#8250df",
}
CAT_NAMES = {
    "closed": "closed weights",
    "open": "open weights (released)",
    "open-unreleased": "open API access, weights not yet released",
    "fleet": "on or near the lab rig",
    "pasteur": "Pasteur IA proxy (served)",
}


def hbar(rows, value_fmt, xmax, xlabel, title, subtitle, outfile, legend, footnote=None):
    L, R, TOP, BAR, GAP, HSCALE = 300, 40, 78, 24, 7, 5.4
    width = 1000
    # legend may need more than one row: pre-compute wrap count for the height
    nrows, lx = 1, 16
    for cat in legend:
        w = 16 + 8 * len(CAT_NAMES[cat]) + 26
        if lx + w > width - 16:
            nrows += 1
            lx = 16
        lx += w
    height = TOP + len(rows) * (BAR + GAP) + 84 + (18 if footnote else 0) + 18 * (nrows - 1)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="DejaVu Sans, sans-serif">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="16" y="30" font-size="19" font-weight="bold" fill="#111">{title}</text>',
        f'<text x="16" y="52" font-size="12.5" fill="#444">{subtitle}</text>',
    ]
    # axis + grid first, so no line crosses the bars or the value labels
    bottom = TOP + len(rows) * (BAR + GAP) - GAP
    parts.append(f'<line x1="{L}" y1="{TOP - 6}" x2="{L}" y2="{bottom}" stroke="#999"/>')
    for step in range(0, int(xmax) + 1, max(1, int(xmax) // 10)):
        if step == 0:
            continue
        x = L + step / xmax * (width - L - R - 90)
        parts.append(f'<line x1="{x:.0f}" y1="{TOP - 6}" x2="{x:.0f}" y2="{bottom}" stroke="#eee"/>')
        parts.append(f'<text x="{x:.0f}" y="{bottom + 14}" font-size="10.5" fill="#666" text-anchor="middle">{step}</text>')
    parts.append(f'<text x="{L + 4}" y="{bottom + 32}" font-size="11" fill="#666">{xlabel}</text>')
    y = TOP
    for label, val, cat in rows:
        w = max(2.0, val / xmax * (width - L - R - 90))
        color = COLORS[cat]
        parts.append(
            f'<rect x="{L}" y="{y}" width="{w:.1f}" height="{BAR}" fill="{color}" rx="2"/>')
        fw = ' font-weight="600"' if cat == "pasteur" else ""
        parts.append(
            f'<text x="{L - 8}" y="{y + BAR / 2 + 4.5}" font-size="12.5" fill="#222" '
            f'text-anchor="end"{fw}>{label}</text>')
        parts.append(
            f'<text x="{L + w + 6:.1f}" y="{y + BAR / 2 + 4.5}" font-size="12" '
            f'fill="#111">{value_fmt(val)}</text>')
        y += BAR + GAP
    # legend
    lx = 16
    ly = height - 34 - 18 * (nrows - 1)
    for cat in legend:
        w = 16 + 8 * len(CAT_NAMES[cat]) + 26
        if lx + w > width - 16:
            lx = 16
            ly += 18
        parts.append(f'<rect x="{lx}" y="{ly}" width="11" height="11" fill="{COLORS[cat]}" rx="2"/>')
        parts.append(f'<text x="{lx + 16}" y="{ly + 9}" font-size="11" fill="#333">{CAT_NAMES[cat]}</text>')
        lx += w
    if footnote:
        # footnote strings are plain text (no & < >), so no escaping needed here
        parts.append(f'<text x="16" y="{height - 8}" font-size="9.5" fill="#666">{footnote}</text>')
    parts.append("</svg>")
    os.makedirs(OUT_DIR, exist_ok=True)
    outfile = os.path.join(OUT_DIR, outfile)
    with open(outfile, "w") as f:
        f.write("\n".join(parts))
    print("wrote", outfile)
    if cairosvg is not None:
        png = outfile.replace(".svg", ".png")
        cairosvg.svg2png(url=outfile, write_to=png, scale=2.0, background_color="white")
        print("wrote", png)
    else:
        print("cairosvg missing: PNG skipped (pandoc PDFs will drop the SVG charts)")


hbar(AA_INDEX, lambda v: f"{v}", 62,
     "Artificial Analysis Intelligence Index v5.0.1 (higher is better)",
     "Flagship models, November 2026: closed vs open weights",
     "Data: Artificial Analysis Intelligence Index v5.0.1, retrieved 2026-11-04 (93 models indexed, 36 open weights).",
     "aa-intelligence-index.svg",
     ["closed", "open", "pasteur", "open-unreleased", "fleet"],
     footnote="The lab's Pasteur IA proxy serves 'big' = GLM-5.3 and 'medium' = GLM-5.3-Flash, both NVFP4 quants; AA measures what each provider serves.")

hbar(COST_PER_TASK, lambda v: f"${v:.2f}", 13.5,
     "USD per Intelligence Index task (lower is better)",
     "What one benchmark task costs, November 2026",
     "Cost per task as published by Artificial Analysis for the same v5.0.1 run; local rig costs only electricity.",
     "cost-per-task.svg",
     ["closed", "open", "pasteur", "open-unreleased", "fleet"],
     footnote="The lab's Pasteur IA proxy serves 'big' = GLM-5.3 and 'medium' = GLM-5.3-Flash, both NVFP4 quants; AA measures what each provider serves.")


# ---------------------------------------------------------------------------
# Helpers for the guide-wide charts (memory budget, quant ladder, DFlash2
# before/after, GPU price per GB). Same conventions as hbar(): hand-rolled
# SVG, no dependencies, plus a 2x PNG because pandoc 3.1.3 silently drops
# SVG when rsvg-convert is absent.

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


SEG_COLORS = {
    "os": "#94a3b8",        # OS + desktop / driver + display duty
    "model": "#3572a5",     # model weights (the GGUF file)
    "vis": "#d29922",       # vision projector (mmproj)
    "ctx": "#2ea043",       # KV cache
    "spd": "#e07b39",       # MTP head, draft model, ubatch buffers
    "free": "#eef1f5",      # unallocated
    "before": "#6b7280",    # decode speed before speculative decoding
    "after": "#2ea043",     # decode speed with DFlash2
    "msrp": "#9e9e9e",      # launch MSRP
    "street-val": "#2ea043",
    "street-std": "#3572a5",
    "street-bad": "#d9534f",
    "unified": "#b0b7c0",   # unified-memory machines (no VRAM), greyed out
    "q16": "#1b5e20", "q8": "#2e7d32", "q6": "#43a047", "q5": "#66bb6a", "q4": "#9ccc65",
    "q9": "#2ea043",        # 9B dense exemplar bars (quant ladder)
    "q35": "#3572a5",       # 35B MoE exemplar bars (quant ladder)
    "fs": "#d9534f",        # flagship weights, out of reach for a home rig
    "sys": "#94a3b8",       # beginner memory budget: system + extras, merged
    "ref": "#9e9e9e",       # single-card reference bars
    "rig": "#2ea043",       # the lab rig's total VRAM
    "fail-real": "#94a3b8",   # failures: non-zero exit (task or environment)
    "fail-fumble": "#d9534f", # failures: model-attributable mis-calls
    "fail-ext": "#d29922",    # failures: external blocks (bot-walls)
    "fail-abort": "#6b7280",  # failures: user aborts
    "spd-served": "#3572a5",  # session speed: lab proxy (served)
    "spd-local": "#2ea043",   # session speed: local rig
    "m-sage": "#2ea043",      # decode by depth: Sage A1.5
    "m-ornith": "#3572a5",    # decode by depth: Ornith-1.5-35B
    "m-tiel": "#8957e5",      # decode by depth: Tiel-Coder-35B
    "m-qwen27": "#d29922",    # decode by depth: Qwen3.8-27B
    "m-flint": "#e07b39",     # decode by depth: Flint
}

LEGEND_TEXT = {
    "os": "OS + desktop", "model": "model file (GGUF)", "vis": "vision projector",
    "ctx": "context cache", "spd": "speed extras", "free": "free",
    "before": "before (plain or MTP)", "after": "with DFlash2",
    "msrp": "launch MSRP", "street-val": "street: value tier",
    "street-std": "street: the rest", "street-bad": "street: 5090 (excluded)",
    "unified": "unified memory (no VRAM)",
    "q9": "Qwen3.8-9B (9B dense)", "q35": "Ornith-1.5-35B-A3B (35B MoE)",
    "fs": "flagship model weights", "sys": "system + extras",
    "ref": "a single big card", "rig": "this guide's rig (28GB)",
    "fail-real": "real: non-zero exit", "fail-fumble": "fumbles: model errors",
    "fail-ext": "external: bot-walls", "fail-abort": "aborts",
    "spd-served": "lab proxy (served)", "spd-local": "local rig",
    "m-sage": "Sage A1.5", "m-ornith": "Ornith-1.5-35B", "m-tiel": "Tiel-Coder-35B",
    "m-qwen27": "Qwen3.8-27B", "m-flint": "Flint",
}


def _svg_head(height, title, subtitle):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" '
        f'viewBox="0 0 1000 {height}" font-family="DejaVu Sans, sans-serif">',
        f'<rect width="1000" height="{height}" fill="#ffffff"/>',
        f'<text x="16" y="30" font-size="19" font-weight="bold" fill="#111">{esc(title)}</text>',
        f'<text x="16" y="52" font-size="12.5" fill="#444">{esc(subtitle)}</text>',
    ]


def _write_svg(parts, outfile):
    parts.append("</svg>")
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, outfile)
    with open(path, "w") as f:
        f.write("\n".join(parts))
    print("wrote", path)
    if cairosvg is not None:
        png = path.replace(".svg", ".png")
        cairosvg.svg2png(url=path, write_to=png, scale=2.0, background_color="white")
        print("wrote", png)
    else:
        print("cairosvg missing: PNG skipped")


def _axis(parts, L, top, bottom, plot_w, xmax, xlabel, step, grid=True):
    parts.append(f'<line x1="{L}" y1="{top - 6}" x2="{L}" y2="{bottom}" stroke="#999"/>')
    if grid:
        for v in range(step, xmax + 1, step):
            x = L + v / xmax * plot_w
            parts.append(f'<line x1="{x:.0f}" y1="{top - 6}" x2="{x:.0f}" y2="{bottom}" stroke="#eee"/>')
    for v in range(step, xmax + 1, step):
        x = L + v / xmax * plot_w
        parts.append(f'<text x="{x:.0f}" y="{bottom + 14}" font-size="10.5" fill="#666" '
                     f'text-anchor="middle">{v}</text>')
    parts.append(f'<text x="{L + 4}" y="{bottom + 32}" font-size="11" fill="#666">{esc(xlabel)}</text>')


def _legend(parts, height, keys):
    lx = 16
    for key in keys:
        parts.append(f'<rect x="{lx}" y="{height - 34}" width="11" height="11" '
                     f'fill="{SEG_COLORS[key]}" rx="2"/>')
        parts.append(f'<text x="{lx + 16}" y="{height - 25}" font-size="11" fill="#333">'
                     f'{esc(LEGEND_TEXT[key])}</text>')
        lx += 16 + 8 * len(LEGEND_TEXT[key]) + 26


def stacked_bars(rows, xmax, xlabel, title, subtitle, outfile, legend_keys, step=4,
                 end_kind=None):
    """rows: (label, [(color_key, value, in_text)], note); one stacked bar per row."""
    L, TOP, BAR, ROWGAP = 340, 78, 22, 16
    plot_w = 1000 - L - 40 - 90
    height = TOP + len(rows) * (BAR + ROWGAP) + 84
    parts = _svg_head(height, title, subtitle)
    y = TOP
    for row_i, (label, segs, note) in enumerate(rows):
        ly = y + BAR / 2 + 4.5
        parts.append(f'<text x="{L - 8}" y="{ly}" font-size="12.5" fill="#222" '
                     f'text-anchor="end">{esc(label)}</text>')
        if note:
            parts.append(f'<text x="{L - 8}" y="{ly + 15}" font-size="10.5" fill="#666" '
                         f'text-anchor="end">{esc(note)}</text>')
        x = L
        free_val = None
        for key, val, intext in segs:
            w = max(1.0, val / xmax * plot_w)
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{BAR}" '
                         f'fill="{SEG_COLORS[key]}" rx="2"/>')
            if intext and w >= 6.2 * len(intext) + 10:
                parts.append(f'<text x="{x + w / 2:.1f}" y="{y + BAR / 2 + 4}" font-size="10.5" '
                             f'fill="#fff" text-anchor="middle">{esc(intext)}</text>')
            if key == "free":
                free_val = val
            x += w
        if end_kind is not None:
            end = end_kind[row_i]
        else:
            end = f"free {free_val:.1f}GB" if free_val else "no headroom"
        parts.append(f'<text x="{x + 6:.1f}" y="{y + BAR / 2 + 4}" font-size="12" '
                     f'fill="#111">{esc(end)}</text>')
        y += BAR + ROWGAP
    _axis(parts, L, TOP, y - ROWGAP, plot_w, xmax, xlabel, step)
    _legend(parts, height, legend_keys)
    _write_svg(parts, outfile)


def bar_rows(rows, xmax, xlabel, title, subtitle, outfile, legend_keys,
             bar_h=12, vlines=(), step=None, rowgap=12):
    """rows: (label, [bars], note); bar = (value, color_key, end_text[, range_to]).
    A 4th tuple element draws a lighter extension up to that value (a measured range)."""
    L, TOP, BG, ROWGAP = 300, 78, 3, rowgap
    plot_w = 1000 - L - 40 - 90
    # total must match the loop's real y-advance (n*(bar_h+BG) + rowgap per row);
    # subtracting BG here undercounted multi-bar rows and squeezed the whole
    # bottom (axis label ran into the legend).
    total = sum(len(b) * (bar_h + BG) + ROWGAP for _, b, _ in rows)
    bottom = TOP + total - ROWGAP
    height = TOP + total + 84
    parts = _svg_head(height, title, subtitle)
    step = step or max(1, int(xmax) // 10)
    # grid behind the bars and their labels, never on top of text
    for v in range(step, xmax + 1, step):
        x = L + v / xmax * plot_w
        parts.append(f'<line x1="{x:.0f}" y1="{TOP - 6}" x2="{x:.0f}" y2="{bottom}" stroke="#eee"/>')
    y = TOP
    for label, bars, note in rows:
        row_h = len(bars) * (bar_h + BG) - BG
        ly = y + row_h / 2 + 4.5
        parts.append(f'<text x="{L - 8}" y="{ly}" font-size="12.5" fill="#222" '
                     f'text-anchor="end">{esc(label)}</text>')
        if note:
            parts.append(f'<text x="{L - 8}" y="{ly + 15}" font-size="10.5" fill="#666" '
                         f'text-anchor="end">{esc(note)}</text>')
        by = y
        for bar in bars:
            val, key, text = bar[0], bar[1], bar[2]
            range_to = bar[3] if len(bar) > 3 else None
            w = max(2.0, val / xmax * plot_w)
            parts.append(f'<rect x="{L}" y="{by}" width="{w:.1f}" height="{bar_h}" '
                         f'fill="{SEG_COLORS[key]}" rx="2"/>')
            if range_to is not None and range_to > val:
                w += max(0.0, (range_to - val) / xmax * plot_w)
                parts.append(f'<rect x="{L}" y="{by}" width="{w:.1f}" height="{bar_h}" '
                             f'fill="{SEG_COLORS[key]}" fill-opacity="0.45" rx="2"/>')
            if text:
                parts.append(f'<text x="{L + w + 6:.1f}" y="{by + bar_h / 2 + 4}" font-size="11.5" '
                             f'fill="#111">{esc(text)}</text>')
            by += bar_h + BG
        y = by + ROWGAP
    for v, vtext in vlines:
        vx = L + v / xmax * plot_w
        parts.append(f'<line x1="{vx:.1f}" y1="{TOP - 8}" x2="{vx:.1f}" y2="{y - ROWGAP}" '
                     f'stroke="#555" stroke-dasharray="5,4"/>')
        parts.append(f'<text x="{vx:.1f}" y="70" font-size="10.5" fill="#555" '
                     f'text-anchor="middle">{esc(vtext)}</text>')
    _axis(parts, L, TOP, y - ROWGAP, plot_w, xmax, xlabel, step, grid=False)
    _legend(parts, height, legend_keys)
    _write_svg(parts, outfile)


# B1: the memory budget picture (advanced 02; the beginner track gets the simplified memory-budget-simple below). Weights = real file
# sizes; context = the hybrid-architecture KV figure from chapter 02; the rig row
# is chapter 02's measured worked example.
MEMORY_BUDGET = [
    ("Laptop, 8GB RAM", [("os", 3.5, ""), ("model", 4.0, ""), ("ctx", 0.5, ""), ("free", 0.0, "")],
     "tiny 3-4B models only; this guide assumes 16GB+"),
    ("Laptop, 16GB RAM", [("os", 4.5, ""), ("model", 7.6, "9B Q6_K"), ("ctx", 1.4, ""), ("free", 2.5, "")],
     "9B class; Q4_K_M is the everyday pick"),
    ("Laptop, 32GB RAM", [("os", 4.5, ""), ("model", 15.2, "35B-A3B MiniPlus"), ("ctx", 1.4, ""), ("free", 10.9, "")],
     "the A3B MoE sweet spot"),
    ("Mac, 32GB (unified)", [("os", 4.5, ""), ("model", 15.2, "35B-A3B MiniPlus"), ("ctx", 1.4, ""), ("free", 10.9, "")],
     "one memory pool, all on GPU"),
    ("Single 16GB GPU (eGPU)", [("os", 0.4, ""), ("model", 14.2, "Sage A1.5"), ("ctx", 1.4, ""), ("free", 0.0, "")],
     "tight; no vision projector"),
    ("The lab rig: 28GB, 2 GPUs", [("os", 1.5, ""), ("model", 14.2, "Sage A1.5"), ("vis", 0.8, "mmproj"),
                                   ("ctx", 1.4, ""), ("spd", 2.1, ""), ("free", 8.0, "")],
     "Sage A1.5 + vision + MTP: ch 02's worked example"),
]

stacked_bars(MEMORY_BUDGET, 32, "gigabytes of memory",
             "What fits in the memory budget",
             "GB per machine; green = context (the model's working memory) at 131k tokens; rig row = chapter 02's measured worked example.",
             "memory-budget.svg",
             ["os", "model", "vis", "ctx", "spd", "free"], step=4)

# B2: the quant ladder, real file sizes from one HuggingFace repo each (9B:
# empero-ai; 35B: the official ornith-ai repo). Two bars per quant level so the
# 35B MoE's extra hardware cost is visible next to the 9B.
QUANT_LADDER = [
    ("BF16 (uncompressed)", [(18.41, "q9", "18.4GB"), (71.07, "q35", "71.1GB")], ""),
    ("Q8_0", [(9.79, "q9", "9.8GB"), (37.80, "q35", "37.8GB")], ""),
    ("Q6_K", [(7.56, "q9", "7.6GB"), (29.21, "q35", "29.2GB")], ""),
    ("Q5_K_M", [(6.64, "q9", "6.6GB"), (25.35, "q35", "25.4GB")], ""),
    ("Q4_K_M", [(5.78, "q9", "5.8GB"), (21.71, "q35", "21.7GB")], "the everyday choice"),
]

bar_rows(QUANT_LADDER, 78, "file size, GB",
         "Two models, five files each: the quant ladder",
         "Sizes as published on HuggingFace, 2026-11-05. The MoE is ~4x heavier per quant.",
         "quant-ladder.svg", ["q9", "q35"], bar_h=20,
         vlines=[(10, "16GB laptop limit"), (28, "rig 28GB")], step=10)

# B3: flagship weights vs the rig, chapter 01's reality check. Sizes as
# published on HuggingFace 2026-11-05: Q4-class quants (Unsloth dynamic) where
# available, the official release for Kimi K3.1 Pro (MXFP4; no GGUF published yet).
FLAGSHIP_WEIGHTS = [
    ("Kimi K3.1 Pro, 2.8T", [(1561, "fs", "1,561GB (56x the rig)")],
     "official MXFP4 release; no GGUF yet"),
    ("Mistral Large 4, ~1T", [(605, "fs", "605GB (22x the rig)")], "unsloth UD-Q4_K_XL"),
    ("DeepSeek V4.1 Flash 1017, 763B", [(501, "fs", "501GB (18x the rig)")], "unsloth UD-Q4_K_XL"),
    ("GLM-5.3, 753B", [(467, "fs", "467GB (17x the rig)")], "unsloth UD-Q4_K_XL"),
    ("GLM-5.3-Flash, 321B", [(200, "fs", "200GB (7x the rig)")], "unsloth UD-Q4_K_XL"),
    ("One refurb 48GB card", [(48, "ref", "48GB")], "RTX A6000 (chapter 12)"),
    ("This guide's rig, 28GB", [(28, "rig", "28GB")], "12GB + 16GB eGPU"),
    ("One 16GB GPU", [(16, "ref", "16GB")], "the Tier A card"),
]

bar_rows(FLAGSHIP_WEIGHTS, 1700, "gigabytes of weights on disk",
         "Why nobody runs the frontier at home",
         "Weights as published on HuggingFace, 2026-11-05: Q4-class Unsloth quants (UD-Q4_K_XL), Kimi's official release. Bars to scale.",
         "flagship-weights.svg", ["fs", "ref", "rig"], bar_h=14, rowgap=26, step=200)

# ---------------------------------------------------------------------------
# Beginner variants (beg01 + beg02): same public sources, fewer bars and
# plainer wording. The advanced charts above carry the full comparisons.

QUANT_LADDER_SIMPLE = [
    ("BF16 (uncompressed)", [(18.41, "q9", "18.4GB")], "the full model"),
    ("Q8_0", [(9.79, "q9", "9.8GB")], ""),
    ("Q6_K", [(7.56, "q9", "7.6GB")], ""),
    ("Q5_K_M", [(6.64, "q9", "6.6GB")], ""),
    ("Q4_K_M", [(5.78, "q9", "5.8GB")], "the everyday choice"),
]

bar_rows(QUANT_LADDER_SIMPLE, 30, "file size, GB",
         "One model, five files",
         "Sizes as published on HuggingFace, 2026-11-05: five compression levels of one model.",
         "quant-ladder-simple.svg", ["q9"], bar_h=22, rowgap=26,
         vlines=[(10, "16GB laptop limit"), (28, "rig 28GB")], step=5)

FLAGSHIP_WEIGHTS_SIMPLE = [
    ("Kimi K3.1 Pro", [(1561, "fs", "1,561GB (56x the rig)")],
     "the official release; no compressed copy yet"),
    ("Mistral Large 4", [(605, "fs", "605GB (22x the rig)")], "a 4-bit compressed copy"),
    ("GLM-5.3-Flash", [(200, "fs", "200GB (7x the rig)")], "a 4-bit compressed copy; the 'small' one"),
    ("This guide's rig", [(28, "rig", "28GB")], "the author's actual rig"),
]

bar_rows(FLAGSHIP_WEIGHTS_SIMPLE, 1700, "gigabytes on disk",
         "The frontier vs your computer",
         "Same scale, no tricks: three frontier models drawn at true size against the lab rig. Data: HuggingFace, 2026-11-05.",
         "flagship-weights-simple.svg", ["fs", "rig"], bar_h=16, rowgap=30, step=200)

MEMORY_BUDGET_SIMPLE = [
    ("Laptop, 16GB RAM", [("sys", 4.5, ""), ("model", 7.6, "9B Q6_K"), ("ctx", 1.4, ""), ("free", 2.5, "")],
     "the everyday 9B"),
    ("Laptop, 32GB RAM", [("sys", 4.5, ""), ("model", 15.2, "35B MoE"), ("ctx", 1.4, ""), ("free", 10.9, "")],
     "the sweet spot"),
    ("A 16GB GPU", [("sys", 0.4, ""), ("model", 14.2, "Sage A1.5"), ("ctx", 1.4, ""), ("free", 0.0, "")],
     "tight: no headroom"),
    ("The lab rig, 28GB", [("sys", 4.4, ""), ("model", 14.2, "Sage A1.5"), ("ctx", 1.4, ""), ("free", 8.0, "")],
     "the author's actual rig"),
]

stacked_bars(MEMORY_BUDGET_SIMPLE, 32, "gigabytes of memory",
             "What fits in the memory budget",
             "What each machine keeps for itself, what the model file takes, what context adds, and what is left over.",
             "memory-budget-simple.svg",
             ["sys", "model", "ctx", "free"], step=4)

# A2: DFlash2 before/after, the measured table from chapter 08 (2026-10-29
# sessions on the dual-GPU rig).
DFLASH2 = [
    ("Flint 15.9GB", [(53, "before", "53"), (73, "after", "73-142", 142)],
     "before: plain decode; acc .24-.77"),
    ("Tiel-Coder-35B", [(44, "before", "44"), (67, "after", "67-75", 75)],
     "before: MTP; acc .19-.24"),
    ("Ornith-1.5-35B", [(40.5, "before", "40.5"), (60, "after", "60-69", 69)],
     "before: MTP, at 86k ctx; acc .23-.29"),
    ("Qwen3.8-27B, long sessions", [(18.7, "before", "18.7"), (24.5, "after", "24.5-29.5", 29.5)],
     "before: MTP; acc .2-.3 to .33"),
    ("Qwen3.8-27B, short chat", [(18.7, "before", "18.7"), (40, "after", "40-68", 68)],
     "same model; acc .2-.3 to .33"),
]

bar_rows(DFLASH2, 145, "decode tok/s (tokens per second)",
         "Speculative decoding on the rig: before and after",
         "Decode speed, dual-GPU rig, 2026-10-29 sessions. acc = acceptance rate. Sage A1.5: DFlash2 measured (61-108, median 76); before pending.",
         "dflash2-before-after.svg", ["before", "after"], bar_h=12, step=20)

# A8: price per gigabyte of memory, launch MSRP vs in-stock street in France
# (2026-11-05, the price table in chapter 12). Ranges are drawn at their low
# end (B50, B65, B70, R9700, A6000, 5090) or midpoint (5060 Ti, 9070 XT); the
# full euro ranges live in the street-price ladder chart below. MSRPs are
# dollar launch figures carried over ~1:1 as euro approximations (EU list
# prices land within ~10% of the dollar number); street prices are the euro
# figures actually checked at French retailers (idealo.fr category sweeps).
# The grey unified-memory rows have no VRAM: the Mac and Strix Halo bars
# divide the whole memory pool (700/16, 3,800/128), the RTX Spark bar divides
# only the GPU-reachable share (7,370/64, the chapter's "~64GB of GPU budget"
# caveat); none of them carries an MSRP bar (one list price each).
GPU_PRICES = [
    ("Strix Halo mini-PC, 128GB", [(29.7, "unified", "€30/GB (128GB ≈€3,800)")], "64GB tier ≈€2,300"),
    ("Intel Arc B580, 12GB", [(20.8, "msrp", "€20.8"), (35.8, "street-val", "€36")], "MSRP ≈€249"),
    ("Intel Arc Pro B50, 16GB", [(21.8, "msrp", "€21.8"), (40.9, "street-val", "€41")], "MSRP ≈€349"),
    ("Intel Arc Pro B60, 24GB", [(20.8, "msrp", "€20.8"), (42.0, "street-val", "€42")], "MSRP ≈€499"),
    ("Apple Silicon Mac, 16GB unified", [(43.8, "unified", "€44/GB (16GB ≈€700)")], "rung 2; quiet, zero install"),
    ("Intel Arc Pro B65, 32GB", [(28.4, "msrp", "€28.4"), (52.5, "street-val", "€53")],
     "listed ≈€909 (US); capacity-first"),
    ("RTX 5060 Ti, 16GB", [(26.8, "msrp", "€26.8"), (54.7, "street-std", "€55")], "MSRP ≈€429"),
    ("AORUS AI BOX (5060 Ti), 16GB", [(62.5, "street-val", "€63/GB")], "€1,000-1,130; box premium"),
    ("Intel Arc Pro B70, 32GB", [(29.7, "msrp", "€29.7"), (64.1, "street-val", "€64")],
     "MSRP ≈€949; often out of stock"),
    ("AMD RX 9070 XT, 16GB", [(37.4, "msrp", "€37.4"), (65.3, "street-std", "€65")], "MSRP ≈€599"),
    ("AMD Radeon AI PRO R9700, 32GB", [(40.6, "msrp", "€40.6"), (67.7, "street-val", "€68")],
     "MSRP ≈€1,299"),
    ("RTX 5070 Ti, 16GB", [(46.8, "msrp", "€46.8"), (82.4, "street-std", "€82")], "MSRP ≈€749"),
    ("RTX A6000, 48GB", [(91.7, "street-std", "€92")], "new ≈€5,250; refurbisher only"),
    ("Dell XPS 16 Creator (RTX Spark), 128GB",
     [(115.2, "unified", "€115/GB of GPU budget (cfg ≈€7,370)")],
     "128GB config; ~half the pool GPU-reachable"),
    ("RTX 5090, 32GB", [(62.5, "msrp", "€62.5"), (248.4, "street-bad", "€248+")], "excluded by rule 3"),
]

bar_rows(GPU_PRICES, 260, "euros per gigabyte of memory (lower is better)",
         "Price per gigabyte of memory, November 2026 (France)",
         "Launch MSRP vs street price, French retailers, 2026-11-05; grey = unified-memory machines (Spark counts only its GPU-reachable share).",
         "gpu-price-per-gb.svg", ["msrp", "street-val", "street-std", "street-bad", "unified"],
         bar_h=12, step=20)

# ---------------------------------------------------------------------------
# Batch 5 (2026-11-05): the visualization-survey picks. ch09 failures split by
# kind and the served-vs-local speed punchline, ch05 decode-by-depth, ch11
# street-price ladder, plus two diagrams (ch03 serving stack, ch04 agent loop).

# ch09: the tier failure table split by kind, per 100 tool calls. Counts are
# the table's own; per-tier end labels use the table's headline rates, segment
# labels are rounded to one decimal.
FAILURES_BY_TIER = [
    ("Pasteur served (151 sessions)", [
        ("fail-real", 4.04, "4.1"), ("fail-fumble", 1.42, "1.4"),
        ("fail-ext", 0.45, "0.5"), ("fail-abort", 0.05, "")], ""),
    ("Ollama Cloud (102 sessions)", [
        ("fail-real", 4.20, "4.2"), ("fail-fumble", 1.45, "1.5"),
        ("fail-ext", 1.50, "1.5"), ("fail-abort", 0.01, "")], ""),
    ("Local rig (70 sessions)", [
        ("fail-real", 3.33, "3.3"), ("fail-fumble", 2.88, "2.9"),
        ("fail-ext", 0.35, ""), ("fail-abort", 0.11, "")], ""),
]

stacked_bars(FAILURES_BY_TIER, 9, "failures per 100 tool calls",
             "Where the failures come from: split by kind",
             "The tier table above, split by kind: real failures land at nearly the same rate on every tier; fumbles and bot-walls differ.",
             "failures-by-tier.svg", ["fail-real", "fail-fumble", "fail-ext", "fail-abort"],
             step=2, end_kind=["6.0 per 100 calls", "7.2 per 100 calls", "6.6 per 100 calls"])

# ch09: the served-vs-local punchline from the averages table, v2 era,
# token-weighted (raw) and tool-corrected.
SPEED_PUNCH = [
    ("Raw: tool time included", [
        (56.5, "spd-served", "56.5"), (22.8, "spd-local", "22.8")], ""),
    ("Tool-corrected", [
        (110.8, "spd-served", "110.8"), (46.1, "spd-local", "46.1")], ""),
]

bar_rows(SPEED_PUNCH, 120, "generated tokens per think-second (~tok/s)",
         "Effective session speed: served proxy vs local rig",
         "v2 era (2026-10-22 onward), 45 served and 19 local sessions; tool-corrected divides out tool-wait time. Data: scripts/mine_runtimes.py.",
         "served-vs-local-speed.svg", ["spd-served", "spd-local"], bar_h=13, step=20)

# ch05: decode speed by context depth. Same session logs as the table above
# (2026-10-29 to 11-05, DFlash2 where a drafter exists); bars at the low end of
# each measured range, lighter segment to the top. CarbonX-14B's one reading
# has no depth attached and is not drawn.
DECODE_DEPTH = [
    ("Shallow (short prompts)", [
        (35.5, "m-sage", "36-135", 134.8), (54.1, "m-ornith", "54-156", 156.1),
        (41.4, "m-tiel", "41-105", 105.3), (45.2, "m-flint", "45-124", 123.5)],
     "n: 807, 25, 27, 31"),
    ("8k-32k", [(88.0, "m-ornith", "88-89", 89.0)], "n: 2"),
    ("32k-80k", [(59.7, "m-flint", "60-76", 76.4)], ""),
    ("Above 80k", [
        (50.3, "m-sage", "50-62", 62.3), (67.2, "m-tiel", "67"),
        (25.5, "m-qwen27", "25.5"), (53.8, "m-flint", "53.8")], "n: 9, 1, 1, 1"),
    ("Near 150k", [(24.0, "m-sage", "24-41", 41.0)], "context scaling alone"),
]

bar_rows(DECODE_DEPTH, 160, "decode tok/s by prompt depth",
         "Decode speed falls with context depth",
         "Per model, Oct-Nov 2026 rig sessions with DFlash2; bars at the low end of the measured range, lighter to the top. n values: see the table above.",
         "decode-by-depth.svg", ["m-sage", "m-ornith", "m-tiel", "m-qwen27", "m-flint"],
         bar_h=12)

# ch11: the street-price ladder. Same price table as the per-gigabyte chart,
# absolute euros this time; bars at the low end, lighter to the top of the
# range. Rung numbers match the chapter's table; rungs 0-1 (already-owned
# laptops) have no purchase price, marketplace used hardware (rule 2) no fixed
# one.
GPU_LADDER = [
    ("Intel Arc B580, 12GB", [(430, "street-val", "€430")], "rung 3; often out of stock"),
    ("Intel Arc Pro B50, 16GB", [(655, "street-val", "€655-850", 850)], "rung 4; the Tier A fleet"),
    ("Apple Silicon Mac, 16GB unified", [(700, "street-std", "from ~€700")], "rung 2; quiet, zero install"),
    ("RTX 5060 Ti, 16GB", [(820, "street-std", "€820-930", 930)], "rung 4; CUDA recipes"),
    ("AMD RX 9070 XT, 16GB", [(930, "street-std", "€930-1,160", 1160)], "rung 4; RDNA4 and ROCm"),
    ("AORUS AI BOX (5060 Ti), 16GB", [(1000, "street-val", "€1,000-1,130", 1130)], "rung 5; Tier A on any laptop"),
    ("Intel Arc Pro B60, 24GB", [(1010, "street-val", "€1,010-1,375", 1375)], "rung 6; 24GB tier"),
    ("RTX 5070 Ti, 16GB", [(1320, "street-std", "€1,320-1,700", 1700)], "16GB CUDA, priced out"),
    ("Intel Arc Pro B65, 32GB", [(1680, "street-val", "€1,680-1,800", 1800)], "rung 7; cheapest 32GB in stock"),
    ("Intel Arc Pro B70, 32GB", [(2050, "street-val", "~€2,050")], "rung 7; often out of stock"),
    ("AMD AI PRO R9700, 32GB", [(2165, "street-val", "~€2,165 when findable")], "rung 7; the compute pick"),
    ("Strix Halo mini-PC, 128GB", [(2300, "street-std", "€2,300-3,900", 3900)], "rung 7b; unified memory"),
    ("RTX A6000, 48GB (refurb)", [(4400, "street-std", "€4,400-5,500", 5500)], "rung 8; refurbisher only"),
    ("Dell XPS 16 Creator (RTX Spark)", [(4419, "street-std", "€4,419-7,370", 7370)], "rung 7b; splits the memory pool"),
    ("RTX 5090, 32GB", [(7950, "street-bad", "€7,950+ (excluded)")], "out: rule 3 above"),
]

bar_rows(GPU_LADDER, 8200, "euros, in-stock street price (lower is better)",
         "The hardware ladder: what a step up costs (France)",
         "In-stock prices at French retailers, 2026-11-05; bars at the low end, lighter to the top of the range. Rung numbers match the table above.",
         "gpu-price-ladder.svg", ["street-val", "street-std", "street-bad"], bar_h=12, step=1000)

# --- diagrams (ch03 serving stack, ch04 agent loop) ------------------------
# Boxes and arrows, same hand-rolled style as the charts. Box text lines are
# kept short enough for their boxes at font-size 12.5 (about 7.6 px per
# character).

def _diagram_head(height, title, subtitle):
    parts = _svg_head(height, title, subtitle)
    parts.append('<defs><marker id="ah" markerWidth="9" markerHeight="7" '
                 'refX="8" refY="3.5" orient="auto">'
                 '<polygon points="0 0, 9 3.5, 0 7" fill="#444"/></marker></defs>')
    return parts


def _dbox(parts, x, y, w, h, lines, stroke, fs=12.5, dash=False):
    dash_attr = ' stroke-dasharray="4,3"' if dash else ''
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
                 f'fill="#ffffff" stroke="{stroke}" stroke-width="1.6"{dash_attr}/>')
    ty = y + h / 2 + 4.5 - (len(lines) - 1) * 8.5
    for ln in lines:
        parts.append(f'<text x="{x + w / 2}" y="{ty:.1f}" font-size="{fs}" fill="#111" '
                     f'text-anchor="middle">{esc(ln)}</text>')
        ty += 17


def _dframe(parts, x, y, w, h, stroke, label=None):
    """A labeled container rect (components are drawn inside it afterwards)."""
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
                 f'fill="#ffffff" stroke="{stroke}" stroke-width="1.6"/>')
    if label:
        parts.append(f'<text x="{x + 8}" y="{y + 15}" font-size="11" font-weight="bold" '
                     f'fill="{stroke}">{esc(label)}</text>')


def _darrow(parts, x1, y1, x2, y2, label="", lx=None, ly=None, dash=False):
    dash_attr = ' stroke-dasharray="4,3"' if dash else ''
    parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#444" '
                 f'stroke-width="1.8"{dash_attr} marker-end="url(#ah)"/>')
    if label:
        mx = lx if lx is not None else (x1 + x2) / 2
        my = ly if ly is not None else (y1 + y2) / 2 - 8
        parts.append(f'<text x="{mx:.1f}" y="{my:.1f}" font-size="10.5" fill="#555" '
                     f'text-anchor="middle">{esc(label)}</text>')


def _dlaptop(parts, x, y, w, h, title):
    """A machine outline: rounded body plus a base bar, title inside the top."""
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" '
                 f'fill="#fbfbfd" stroke="#999" stroke-width="1.4"/>')
    parts.append(f'<rect x="{x + w * 0.28:.0f}" y="{y + h - 8:.0f}" width="{w * 0.44:.0f}" '
                 f'height="8" rx="3" fill="#d7dce3"/>')
    parts.append(f'<text x="{x + w / 2}" y="{y + 17}" font-size="11.5" font-weight="bold" '
                 f'fill="#333" text-anchor="middle">{esc(title)}</text>')


def _delbow(parts, pts, label="", lx=None, ly=None):
    """A multi-segment arrow; the arrowhead lands on the last segment's end."""
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        marker = ' marker-end="url(#ah)"' if i == len(pts) - 2 else ''
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#444" '
                     f'stroke-width="1.8"{marker}/>')
    if label:
        mx = lx if lx is not None else sum(p[0] for p in pts) / len(pts)
        my = ly if ly is not None else sum(p[1] for p in pts) / len(pts) - 8
        parts.append(f'<text x="{mx:.1f}" y="{my:.1f}" font-size="10.5" fill="#555" '
                     f'text-anchor="middle">{esc(label)}</text>')


def diagram_serving_stack():
    parts = _diagram_head(536, "The serving stack, mechanically: where the model lives",
        "The same server and API on three machines; what differs is where the weights sit and who does the math.")
    _dbox(parts, 690, 62, 284, 40, ["Your browser", "the built-in chat page"], "#3572a5")
    _dbox(parts, 690, 110, 284, 40, ["OpenCode (ch 04)", "reads and edits files"], "#3572a5")
    _dbox(parts, 690, 158, 284, 40, ["MCP tool servers (ch 07)", "search, PubMed, more"], "#3572a5")
    _dbox(parts, 330, 96, 300, 104, ["llama-server", "one process, one port",
                                     "OpenAI-compatible API"], "#2ea043")
    _darrow(parts, 630, 118, 690, 82)
    _darrow(parts, 630, 148, 690, 130)
    _darrow(parts, 630, 178, 690, 178)
    parts.append('<line x1="499" y1="200" x2="499" y2="224" stroke="#444" stroke-width="1.8"/>')
    parts.append('<line x1="169" y1="224" x2="829" y2="224" stroke="#444" stroke-width="1.8"/>')
    parts.append('<text x="660" y="218" font-size="10.5" fill="#555" text-anchor="middle">'
                 'runs on one of these</text>')
    _darrow(parts, 169, 224, 169, 240)
    _darrow(parts, 499, 224, 499, 240)
    _darrow(parts, 829, 224, 829, 240)
    # Panel A: CPU-only laptop
    _dlaptop(parts, 16, 240, 306, 262, "CPU-only laptop (9B class)")
    _dbox(parts, 30, 280, 92, 40, ["GGUF file", "on SSD"], "#d29922", fs=11.5)
    _darrow(parts, 76, 320, 76, 356, "loaded at startup", lx=150, ly=342)
    _dbox(parts, 30, 356, 130, 48, ["DRAM", "model + context"], "#3572a5", fs=11.5)
    _dbox(parts, 190, 356, 118, 48, ["CPU", "does the math"], "#e07b39", fs=11.5)
    _darrow(parts, 160, 380, 190, 380, "math", lx=175, ly=372)
    parts.append('<text x="169" y="498" font-size="10.5" fill="#555" text-anchor="middle">'
                 '9B class: ~5-12 tok/s (est.)</text>')
    # Panel B: laptop + discrete GPU (the guide's Tier A rig)
    _dlaptop(parts, 346, 240, 306, 262, "Laptop + discrete GPU (Tier A)")
    _dbox(parts, 360, 280, 92, 40, ["GGUF file", "on SSD"], "#d29922", fs=11.5)
    _darrow(parts, 406, 320, 406, 340, "layers that fit", lx=480, ly=334)
    _dframe(parts, 360, 340, 150, 64, "#2ea043", label="GPU (does the math)")
    _dbox(parts, 368, 360, 134, 36, ["VRAM", "weights + context"], "#2ea043", fs=11)
    _darrow(parts, 435, 404, 435, 424, "optional, 5-6x slower", lx=505, ly=418, dash=True)
    _dbox(parts, 360, 424, 150, 40, ["DRAM overflow", "layers that don't fit"],
          "#3572a5", fs=11, dash=True)
    _darrow(parts, 510, 444, 530, 444, dash=True)
    _dbox(parts, 530, 424, 108, 40, ["CPU", "does the math"], "#e07b39", fs=11.5)
    parts.append('<text x="499" y="484" font-size="10.5" fill="#555" text-anchor="middle">'
                 'all layers on GPU: 60-140 tok/s measured</text>')
    parts.append('<text x="499" y="498" font-size="10.5" fill="#555" text-anchor="middle">'
                 'CPU layers: ~80GB/s DDR5 vs ~448GB/s VRAM, 15-25 tok/s</text>')
    # Panel C: unified memory (Mac, Strix Halo, RTX Spark)
    _dlaptop(parts, 676, 240, 306, 262, "Unified memory (Mac, Strix Halo, Spark)")
    _dbox(parts, 690, 280, 92, 40, ["GGUF file", "on SSD"], "#d29922", fs=11.5)
    _darrow(parts, 736, 320, 736, 346, "loaded", lx=796, ly=336)
    _dbox(parts, 690, 346, 160, 54, ["Unified memory", "RAM = VRAM, one pool"], "#2ea043", fs=11.5)
    _dbox(parts, 880, 338, 88, 34, ["CPU", "does the math"], "#e07b39", fs=11)
    _dbox(parts, 880, 378, 88, 34, ["GPU", "does the math"], "#e07b39", fs=11)
    _darrow(parts, 850, 358, 880, 355)
    _darrow(parts, 850, 388, 880, 395)
    parts.append('<text x="829" y="484" font-size="10.5" fill="#555" text-anchor="middle">'
                 'laptops and mini PCs</text>')
    parts.append('<text x="829" y="498" font-size="10.5" fill="#555" text-anchor="middle">'
                 'Spark: GPU gets a fixed slice (~half)</text>')
    _write_svg(parts, "serving-stack.svg")


def diagram_agent_loop():
    parts = _diagram_head(470, "The agent loop: how OpenCode works a task",
        "One prompt becomes many model round-trips; the loop can even change its own configuration along the way.")
    _dbox(parts, 330, 76, 320, 58, ["You: a prompt in the project folder"], "#94a3b8")
    _dbox(parts, 330, 162, 320, 66, ["OpenCode", "gathers files, AGENTS.md, config"], "#3572a5")
    _dbox(parts, 330, 256, 320, 66, ["The model", "(the llama-server from ch 03)"], "#2ea043")
    _dbox(parts, 716, 250, 258, 78, ["Tools run: read, edit, bash,",
                                     "install, configure, spawn"], "#d29922")
    _dbox(parts, 330, 372, 320, 66, ["The answer", "real edits on disk, a diff you can check"], "#6b7280")
    _dbox(parts, 716, 372, 258, 56, ["Or a subagent:", "its own smaller loop"], "#d29922", dash=True)
    _darrow(parts, 490, 134, 490, 162)
    _darrow(parts, 490, 228, 490, 256)
    _darrow(parts, 490, 322, 490, 372)
    _darrow(parts, 650, 274, 716, 274, "tool call", lx=683, ly=266)
    _darrow(parts, 716, 306, 650, 306, "result: repeat", lx=683, ly=320)
    _delbow(parts, [(760, 250), (760, 190), (650, 190)], "config changes feed back",
            lx=770, ly=184)
    _darrow(parts, 845, 328, 845, 372, "spawns one", lx=902, ly=352)
    _write_svg(parts, "agent-loop.svg")


diagram_serving_stack()
diagram_agent_loop()
