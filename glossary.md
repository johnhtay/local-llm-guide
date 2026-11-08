# Glossary (advanced track)

Every abbreviation and non-standard term used in this guide, one line each.
Beginners get the same list in plainer words: [beginner/glossary.md](beginner/glossary.md).

## Models and files

| Term | Meaning |
|---|---|
| GGUF | Single-file quantized model format used by llama.cpp |
| safetensors | Original full-precision weight format; for training, not for llama.cpp |
| mmproj | The small vision-projector GGUF that enables image input |
| imatrix | Importance-matrix calibration data used to build low-bit quants with less damage |
| Quant levels (Q4_K_M, Q5_K_M, IQ4_XS, IQ3_XXS, IQ2_XS) | Names for quantization levels; nominal ~4.8, 5.7, 4.3, 3.1, 2.1 bits per weight respectively. **Not hard-set**: actual file size depends on each model's architecture (layer count, expert count, vocab size, embedding ratio, GQA ratios), so the same quant label can differ by tens of percent between models. The tutorial's examples are pinned to Qwen3.8-9B and Ornith-1.5-35B |
| bpw | Bits per weight; average precision of the quant |
| Requant / mixed recipe | A custom re-quantization that blends levels across tensors (e.g. the fleet's APEX-I-MiniPlus family, ~3.5bpw average) |

## Architecture

| Term | Meaning |
|---|---|
| MoE (Mixture of Experts) | Architecture with many expert blocks; only a few are active per token |
| A3B | "Active ~3B": only about 3 billion parameters fire per token in that MoE |
| Active params | The parameters actually touched per token; they set decode speed |
| Dense | Every parameter active per token (contrasted with MoE) |
| FFN | Feed-forward network: the per-layer MLP block, the bulk of MoE weights |
| GQA | Grouped-query attention: fewer KV heads than query heads, smaller KV cache |
| Hybrid (GDN/SSM) | Mix of linear-attention/state-space layers with a few full-attention layers; per-layer state replaces per-token KV, enabling very long context cheaply |
| KV cache | Stored key/value states for the context; the main per-token memory cost |
| MTP | Multi-token prediction: next-token head(s) baked into the GGUF, used for speculative decoding |
| DFlash2 | Speculative-decoding scheme using a separate small drafter GGUF; the llama.cpp implementation of DFlash (arXiv 2602.06036), whose block-diffusion drafter proposes a whole block of tokens per pass |
| DSpark | Next speculative-decoding framework (arXiv 2607.05147): a semi-autoregressive drafter (parallel backbone plus a light sequential module) with confidence-scheduled verification; the future-project upgrade path for this fleet |
| EAGLE-3 | Previous-generation speculative-decoding family: an autoregressive drafter conditioned on the target model's features; the baseline DFlash compares itself against |
| Drafter | The small model that proposes tokens for the big model to verify |
| Acceptance rate | Fraction of drafted tokens the big model accepts; sets the speedup |

## llama.cpp serving

| Term | Meaning |
|---|---|
| Prefill | Processing the prompt before output starts (compute-bound) |
| Decode | Generating output tokens (bandwidth-bound) |
| tok/s | Tokens per second of output (decode speed) |
| Token-weighted mean | Sum of tokens divided by sum of generation time: one number for a whole tier, big sessions count more |
| Tool-corrected tok/s | Tokens divided by generation time minus tool time: an upper bound on decode speed, since prefill stays in |
| pp512 / tg32 / tg128 | llama-bench metrics: prompt processing at batch 512; token generation at batch 32 or 128; the larger batch reads higher |
| Gen tok | Generated tokens in a session: output plus reasoning; the served chapter 09 table shows it next to its split (Reason tok, Out tok), the local table shows the total only |
| Reason tok | Reasoning (thinking) tokens as the provider's usage ledger reports them; a zero means the ledger did not split them, not that the model did not think |
| Out tok | The ledger's output tokens: final prose plus tool-call syntax; for llama-server sessions this also holds the thinking, which the ledger does not split out |
| `-c` / context | Context length in tokens |
| `-ngl` / NGL | Number of layers offloaded to GPU; 99/999 means all |
| `-ub` / ubatch | Prefill batch size; bigger = faster prefill, more peak memory; decode unaffected |
| `-ctk/-ctv q8_0` | KV cache quantization; halves cache memory |
| `-sm layer` | Multi-GPU split mode: only activations cross the bus (fast); tensor/row modes are slower |
| `-dev CUDA0,CUDA1` | GPU placement order |
| `-devd` / `-ngld` | Device and layer pins for the drafter model |
| `--ctx-checkpoints` | Divergence-recovery checkpoints; restore instead of full re-prefill |
| `--cache-reuse` | KV shifting to reuse cache after edits; inert when a vision projector is loaded |
| Acceptance | Share of drafter-proposed tokens the big model keeps; sets the speculative-decoding speed-up |
| Shallow | Short prompts (a few hundred tokens), where decode is fastest |
| FlashAttention (`-fa`) | Fused attention kernel; on for any GPU run |
| VRAM | Graphics-card memory; the fast memory a model runs in |
| RAM | System memory; what CPU-only runs use |
| OOM | Out of memory: the run aborts because it exceeded the memory budget |
| CUDA | NVIDIA's GPU computing stack; a "CUDA device" is an NVIDIA GPU |
| USB4 | The dock standard connecting the eGPU to the laptop |
| TUI | Terminal user interface: a text-mode application |
| npm | The Node.js package registry and its installer; how OpenCode plugins ship |
| Token | A word piece; models read and write tokens, not letters |
| Prompt | The input message sent to the model |
| Span med | Median generation span of one assistant message, request to last streamed token: prefill, decode, and provider latency inside. The OpenCode database stamps the stream's end, not the first token, so it is a per-call cost figure, not a responsiveness figure |
| Q&A | Questions and answers; in the chapter 09 task-type table, general chat sessions (asking, catching up on news) that fit no other type |
| F16 | Full 16-bit precision, unquantized |
| BF16 | Brain float 16: the usual 16-bit training format; "uncompressed" in the quant ladder |
| Ollama | Model runtime; its hosted service (Ollama Cloud) served every Ollama-labelled run in this guide |
| Ollama Cloud | Ollama's hosted inference: the same API, the models run on their servers; used here to benchmark open models too large for the rig |
| OpenRouter | Metered API reselling ~450 models (open and closed) through one OpenAI-compatible key; no subscription |
| Le Chat (Vibe) | Mistral's chat product; Pro at $14.99/mo (renamed "Vibe" in 2026); the cheapest major chat subscription |
| Strata | An alternative engine used to serve very large quantized models from disk |
| Vulkan | Cross-vendor GPU interface; llama.cpp's fallback backend on non-NVIDIA GPUs |
| NVFP4 | NVIDIA's 4-bit floating-point quantization format |
| MXFP4 | Microscaling 4-bit: a 4-bit floating-point weight format; Kimi K3.1 Pro's official release ships in it |
| UD-Q4_K_XL | Unsloth Dynamic Q4_K_XL: a mixed-precision 4-bit quant recipe published by the Unsloth quantizers |
| WSL / WSL2 | Windows Subsystem for Linux: a Linux environment inside Windows |
| Pasteur IA | The Institut Pasteur AI service; the endpoint the LiteLLM proxy fronts |
| Launcher env vars (CTX, NP, PORT, UB, NMAX, MTPOK, NODRAFT) | Values the Windows launch scripts read at start: context size, parallel request slots, port, ubatch, drafter proposal length, MTP on/off, drafter off |
| JSONC | JSON with comments allowed; OpenCode's config file format |
| API | The way programs talk to each other over a network; an "OpenAI-compatible API" is one speaking that shape |
| eGPU | External GPU in an enclosure (here: USB4 dock) |
| AI BOX | Gigabyte's AORUS finished eGPU enclosure line; the lab's unit is the RTX 5060 Ti AI BOX, 850 W PSU, TB5/USB4 |
| TB4 | Thunderbolt 4: the older name for the same class of cable standard as USB4 |
| TB5 | Thunderbolt 5: the newer, faster version of the same cable standard |
| OCuLink | PCIe-over-a-cable connector on some eGPU docks; no hot-swap, and a Thunderbolt-only host falls back to the dock's USB4 port |
| Battlemage | Intel's current GPU architecture (Xe2); consumer Arc B580/B570, workstation Arc Pro B50 (16GB), B60 (24GB), B65 (32GB), B70 (32GB) |
| RDNA4 | AMD's current GPU architecture; RX 9070 series (16GB) and Radeon AI PRO R9700 (32GB workstation card) |
| ROCm | AMD's GPU compute stack, the AMD equivalent of CUDA |
| SYCL | The open GPU compute stack llama.cpp uses on Intel Arc |
| OpenVINO / OVMS | Intel's inference runtime and its model server; sometimes faster than llama.cpp's SYCL on Arc |
| Mesa-ANV | The open-source Linux Vulkan driver for Intel GPUs; can lag the Windows driver badly (the source of a 3.3 t/s outlier in the hardware doc) |
| GRIMOIRE | A third-party native C++/SYCL inference engine for Arc (MXFP4 weights); not llama.cpp, so its numbers are not comparable to llama.cpp rows |
| SR-IOV | One physical GPU partitioned into several virtual GPUs for containers or VMs |
| SFF | Small form factor: low-profile, low-power card format |
| Refurbisher | A business that buys decommissioned fleet hardware in bulk, tests and refurbishes it, and resells with warranty |
| Unified memory | One memory pool shared by CPU and GPU (Apple Silicon, Strix Halo, RTX Spark); no split math needed. On Windows RTX Spark systems only about half of the pool is GPU-reachable by default; Strix Halo exposes most of it (board-dependent) |
| Mtok | Million tokens: the unit API pricing is quoted in |
| kWh | Kilowatt-hour: the unit on an electricity bill |
| MSRP | Manufacturer's suggested retail price: the launch list price |
| Capex | Capital expenditure: hardware bought up front, as opposed to per-use fees |
| WDDM | Windows display driver model; its eviction and display duty eat VRAM margins |
| DWM | Windows' desktop compositor; it holds VRAM on whichever GPU drives the display |
| Strix Halo | AMD's Ryzen AI Max APU codename (the 395 flagship, the 390, and the newer 388/392 SKUs): CPU and GPU on one chip, 32-128GB soldered LPDDR5X, ~256GB/s; sold in mini-PCs and laptops |
| RTX Spark | NVIDIA's unified-memory chip family for PCs: GB10 (DGX Spark desktops) and N1X (laptops and mini PCs, such as the Dell XPS 16 Creator); Blackwell RTX GPU and CPU on one die, native CUDA |
| Abliterated | Fine-tune that strips a model's refusal/alignment behaviour; a community variant class, not an official release |
| APEX-I-MiniPlus / NanoPlus | IsValorum's mixed-requant recipes: per-tensor precision with MoE experts locked at IQ3_XXS; MiniPlus ~14-15GB (the Tier A size), NanoPlus ~11.5-12.3GB (16GB-card size) |

## Agents and infrastructure

| Term | Meaning |
|---|---|
| LLM | Large language model: what "the model" means throughout this guide |
| Open weights | The model file itself is free to download and run; you still owe nothing per query |
| OpenCode | The terminal coding agent used with the local servers |
| MCP | Model Context Protocol: a standard for giving models external tools |
| MCP server | One set of tools exposed over MCP (e.g. PubMed's twelve research tools) |
| Skills | On-demand instruction packs (`SKILL.md`) the agent loads when relevant |
| Plugins | npm packages that hook or extend OpenCode (agent-memory, Ponytail) |
| Ponytail | Plugin enforcing minimal-change coding with a mandatory "what I did not check" closing |
| OpenAI-compatible | Any server speaking the `/v1/chat/completions` API shape |
| LiteLLM | Local proxy fronting authorized cloud endpoints behind one key |
| SearXNG | Self-hosted meta-search engine; the web-search MCP's preferred provider, no API keys |
| ia.pasteur.cloud | The Institut Pasteur AI endpoint the proxy fronts |
| Prompt caching | Vendors discount tokens already seen earlier in the session (often 50-90% off input); agent sessions benefit most |
| Data residency | Which jurisdiction stores and processes data; European residency simplifies institutional compliance |
| Rubric | A checklist of pass/fail questions used to grade a submission against a stated standard |
| DOE | US Department of Energy, whose national laboratories set the Into the Unknown rubrics |

## Benchmarks (all provider-published unless noted)

| Term | Meaning |
|---|---|
| n | Number of generations (individual model outputs) a measurement averages over |
| TB2.1 | Benchmark row in the lab's model-comparison table (agentic tasks); full definition lives in the lab's bench notes, not here |
| MCP-Atlas | Benchmark row in the lab's model-comparison table (tool use over MCP servers); full definition lives in the lab's bench notes |
| GPQA-D | GPQA-Diamond: graduate-level science questions |
| AIME | American Invitational Mathematics Examination: a competition-math benchmark used as a reasoning-model row |
| BrowseComp | Benchmark for browsing-and-retrieval tasks |
| GAIA | General assistant benchmark with multi-step tool use |
| SciCode | Research-level scientific coding benchmark |
| HLE | Humanity's Last Exam: very hard expert questions |
| HLE-Diamond | The Diamond (hardest) subset of HLE; replaced plain HLE in the AA index from v5 |
| OmniDocBench | Document-parsing benchmark (PDF and image to text) |
| Artificial Analysis (AA) | Independent benchmarking shop; publishes the Intelligence Index, cost and speed per model |
| Intelligence Index | AA's composite capability score (0-100); current version v5.0.1 (2026-10-27), nine evaluations, ~60% private |
| Progress Index | AA's single continuous scale tracking capability across model generations (launched with v5) |
| Private test set | Evaluation questions withheld from public release so they cannot be memorized from training data |
| Contamination | A public benchmark ending up in training corpora, so scores measure memorization, not ability |
| Reasoning-effort tier | The (low)/(medium)/(high)/(max) thinking-budget settings of reasoning models; higher effort costs more and scores higher |
| FrontierCode 2.0 | Cognition's private coding benchmark in AA's index; graded on whether a repo maintainer would merge the change |
| Terminal-Bench-Science | 70 agentic scientific research tasks run in a terminal (new in AA index v5) |
| AutomationBench-AA | AA's agentic workflow-automation benchmark (added in v4.3) |
| Claw-Eval | Autonomous-agent benchmark with tool-use and user-agent splits (used by Occamy's paper); "pass3" = all three independent runs must pass |
| WildClawBench | Harder autonomous-agent benchmark from the same family; real-world tool workflows |
| tau3-Bench | Multi-turn tool-use benchmark (banking scenario in the Occamy table) |
| GDPval | OpenAI's real-world economically valuable task suite; the Occamy number is the paper's own reproduction, not the official leaderboard |
| FrontierScience | Olympiad-level (FS-Olympiad) vs PhD-level research (FS-Research) subtasks in physics, chemistry and biology, used by the Axion and Sage papers |
| Co-work | Office, commerce and automation agent work; the mission Occamy's paper trains for, as opposed to scientific reasoning |
| Best-of-runs | Reporting the best score of several independent runs; the most generous benchmark protocol, and the one Axion's paper uses |
| Presence penalty | Sampling setting that discourages repeating tokens already generated; the counter-measure applied to Axion's loops |
| dwm-edge | State where the desktop window manager (dwm) and the model's VRAM use together saturate a GPU's memory (96%/96% observed); the suspect behind the 11-06 crash |
| AA-Briefcase, AA-Omniscience, GDP.pdf, CritPt | The other evaluations in AA index v5.0.1: business analysis, knowledge breadth, a long economic report, research-level physics |
| API-only model | A model served through an API whose weights are not released (AA marks these on its leaderboard) |
| Agentic | A setup where the model drives tools, files or a terminal itself, instead of only answering a prompt |
| Metal | Apple's GPU interface; llama.cpp uses it on Macs |

## Lab and science terms

| Term | Meaning |
|---|---|
| BEAST X / BEAST 2 | The phylogenetics programs the lab uses; model files are XML |
| BEASTX skills | The lab's instruction packs (SKILL.md files) for writing BEAST XML correctly |
| XML | Text format with nested tags; BEAST model files are XML |
| MCMC | Markov chain Monte Carlo: the sampler behind Bayesian phylogenetics |
| Plate diagram | The graphical-model notation used by PhyloPlate (Hoehna et al. 2014) |
| tMRCA | Time to the most recent common ancestor of a sampled set |
| CI | Credible interval: the Bayesian analogue of a confidence interval |
| MAE | Mean absolute error |
| LOOCV | Leave-one-out cross-validation: predict each held-out tip from the rest |
| R2pred | Predictive R-squared: how well a model predicts held-out values |
| TN93 | Tamura-Nei 1993 DNA substitution model; "union-of-masks" is a fast approximation of it |
| PMC / BioC OA | PubMed Central open-access full text in the BioC structured format |
| DOI | Digital object identifier for a paper |
| PMCID | PubMed Central record identifier |
| OA | Open access: papers whose full text anyone can read and download |
| OpenAlex | Open scholarly database used here for citation metrics |
| bioRxiv / preprint | A paper posted before peer review (bioRxiv is the biology server) |
| MMM | Markov-modulated model: branch rates switch between hidden states |
| Episodic clock | Molecular clock where rates change between episodes rather than smoothly |
| DENV / CHIKV | Dengue virus / chikungunya virus, the MOSAIC project's arboviruses |
| MOSAIC | The PhD project: MMM plus episodic clocks for DENV/CHIKV host switching |
| MTBD / structured coalescent / scotti | Competing models for inferring pathogen host jumps |
| BDMMprime / MSC | BEAST packages: birth-death multi-type trees / multiespecies coalescent |
| Identifiability | Whether a model's parameters can be recovered from data at all |
| Out-of-distribution | Input far from a model's training data, where its published accuracy does not transfer |
| Canary / anti-distillation | Hidden marker strings planted in outputs to detect model copying |
