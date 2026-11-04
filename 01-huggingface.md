# 01 — HuggingFace in ten minutes

[HuggingFace](https://huggingface.co) is the model zoo. New open-weights models are
pushed **daily**; you need exactly three skills: find, judge, download.

## Anatomy of a model repo

- **Model card** — architecture, context length, license, benchmark table. Read it.
- **Files and versions** tab — the actual weights. Two kinds:
  - `safetensors` — original (full-precision) weights. For training/fine-tuning or
    frameworks that quantize on the fly. **Not** what llama.cpp runs.
  - `.gguf` — quantized single-file weights for llama.cpp (and friends). **This is what
    you want.** Several sizes per model, named by quant level.

## Quant levels — how much quality per byte

| Name | ~bpw | 9B model ≈ | 35B model ≈ | Use when |
|---|---|---|---|---|
| Q8_0 | 8.5 | 9.6GB | 37GB | Near-lossless; overkill for chat |
| Q6_K | 6.6 | 7.4GB | 29GB | Quality-critical, memory to spare |
| Q5_K_M | 5.7 | 6.5GB | 24GB | Good default on 32GB+ machines |
| **Q4_K_M** | 4.8 | **5.5GB** | 21GB | **The everyday default** |
| IQ4_XS | 4.3 | 4.9GB | 19GB | Slightly tighter than Q4, small quality cost |
| IQ3_XXS | 3.1 | 3.6GB | 14GB | Last stop before real degradation |
| IQ2_XS | 2.1 | 2.4GB | 9GB | Only for huge-MoE-on-tiny-VRAM stunts |

Rules of thumb: **Q4_K_M is the default choice**; drop to IQ4_XS when ~1GB short;
below Q3 quality falls off fast (IQ2_XS is a party trick, not a daily driver).
Community *mixed recipes* (e.g. the APEX-I-MiniPlus requants in our fleet) blend
levels across tensors — ~3.5bpw average with near-Q4 quality at ~15GB for 35B models.

**Imatrix quants** (labels like `IQ4_XS` from a quantizer with an imatrix note) use a
calibration corpus to protect quality at low bpw — prefer them over plain quants at
the same level.

## A 4-step download decision

1. **Trust the source.** Official org uploads or established quantizers
   (bartowski, Unsloth) — consistent, tested quants. A random first-time uploader
   at Q2 is a gamble.
2. **Check the card's own benchmark table.** No table, no trust.
3. **Pick size by memory budget** — the arithmetic is in [02-hardware-fit.md](02-hardware-fit.md).
4. **Check the license.** Apache-2.0 and MIT are permissive; research licenses may
   block commercial use.

**Vision models** ship a second small file, usually named `*mmproj*.gguf` — download
it alongside if you want image input.

**Draft models** (small `*-draft*.gguf` files) are for speculative decoding speed-ups —
see [03-llamacpp-server.md](03-llamacpp-server.md).

## Keeping current without FOMO

- *Explore → Trending* for the weekly pulse; filter by **GGUF** and parameter size.
- New flagship releases land constantly; a fresh release is **rarely** worth
  re-verifying your whole stack. Our vetted shortlist lives in
  [05-fleet-2026-11.md](05-fleet-2026-11.md) — refresh it monthly, not daily.
- Search tip: in the *Models* tab, filter Type → GGUF, then sort by downloads or
  trending; sort "Recently updated" only if you are hunting a fix.
