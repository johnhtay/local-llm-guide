# 05: Which model, exactly?

Picks verified by the lead tester in November 2026. Names change monthly; when in
doubt, re-check this list or ask the lead tester.

| Your machine | Model | What to search on HuggingFace | File size |
|---|---|---|---|
| 16GB RAM laptop | Qwen3.8-9B | "Qwen3.8-9B GGUF", file `Q5_K_M` | ~6.5GB |
| 32GB RAM laptop | Sage A1.5 or Ornith-1.5-35B | "Sage A1.5 GGUF" or "Ornith-1.5-35B GGUF" (MiniPlus requant) | ~15GB |
| Mac 32GB+ | same as 32GB laptop | same files | ~15GB |
| eGPU dock / GPU | Sage A1.5 | same file, plus its `mmproj` file if you want images | ~15GB |

## Reading the names

- The number (9B, 35B) is the model's size in billions of parameters. Bigger is
  smarter but slower and needs more RAM.
- "Q5_K_M", "Q4_K_M" and friends are compression levels; see chapter 01.
- Sage, Ornith, and the Qwen3.8 family are all open-weights and Apache/MIT-style
  licensed, fine for research use.

## If you only remember one thing

32GB RAM or more: take Sage A1.5. Less: take the 9B. It really is that simple for a
first setup.

The full ranked fleet with measured speeds and honest caveats lives in the advanced
guide ([../05-fleet-2026-11.md](../05-fleet-2026-11.md)).
