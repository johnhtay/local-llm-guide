# Running Open-Weights LLMs Locally — A Practical Guide

For lab colleagues who want a fully local assistant (coding agent + models) with no
cloud dependency. Everything here is verified on the lead tester's rig as of
**2026-11-04**: RTX 4080 Laptop 12GB + RTX 5060 Ti 16GB eGPU (28GB total), plus
plain-CPU checks. What runs on that rig runs on anything in the same memory class —
and the same thinking covers other hardware.

## The files, in reading order

| File | What it teaches | Time |
|---|---|---|
| [01-huggingface.md](01-huggingface.md) | Finding and choosing model files (GGUF, quant levels) — deliberately brief | 10 min |
| [02-hardware-fit.md](02-hardware-fit.md) | The arithmetic: will this model fit and run on my hardware? | 15 min |
| [03-llamacpp-server.md](03-llamacpp-server.md) | Serving a model with `llama-server`; real launch recipes per tier | 20 min |
| [04-opencode.md](04-opencode.md) | OpenCode: providers, MCP, skills, plugins; local + LiteLLM-proxied models side by side | 30 min |
| [05-fleet-2026-11.md](05-fleet-2026-11.md) | The vetted fleet, ranked — what to actually run today | 10 min |

## The one-page decision table

| Your hardware | Free memory | Run (fleet picks in 05) | Output speed |
|---|---|---|---|
| CPU-only laptop, 16GB RAM | ~10GB | 9B-class Q4/Q5 (e.g. Qwen3.8-9B Q5_K_M, ~6.5GB) | ~5–12 tok/s (est.) |
| CPU-only laptop, 32GB RAM | ~26GB | 35B-A3B MoE MiniPlus (~15GB) | ~15–25 tok/s (est.) |
| MacBook, M-series Pro/Max, 32GB | unified | 35B-A3B MoE MiniPlus, all layers on GPU | ~40–80 tok/s (est.) |
| MacBook, M-series, 48GB | unified | same + much longer context | ~40–80 tok/s (est.) |
| eGPU dock / GPU, 16GB VRAM | 16GB | 35B-A3B MiniPlus, full offload + MTP | ~40–70 tok/s (est.) |
| Dual GPU (12+16GB) or 32GB VRAM | 28GB | whole Tier-A fleet, 229–262k context, DFlash2 | 60–140 tok/s (measured) |

Speeds depend on model (MoE *active* parameters matter — see 02) and context length.

## Notation and honesty rules

- **tok/s** = generated tokens per second during output (decode speed).
- **bpw** = bits per weight (quantization density; more = better quality, bigger file).
- **(measured)** numbers come from the lead tester's dual-GPU rig on llama.cpp b11803,
  Nov 2026. **(est.)** numbers are bandwidth-based estimates — verify on your machine.
- Benchmark scores in 05 are provider-published, not independently replicated.

## Printing

```sh
pandoc README.md 01-huggingface.md 02-hardware-fit.md 03-llamacpp-server.md 04-opencode.md 05-fleet-2026-11.md \
  -o local-llm-guide.pdf --pdf-engine=xelatex -V mainfont="DejaVu Serif"
```
