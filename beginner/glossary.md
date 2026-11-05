# Glossary (beginner track)

Every new word used in this track, explained in one line. If a word is missing,
tell the lead tester and it will be added.

| Word | Meaning |
|---|---|
| Model (LLM) | A very large text-prediction program, stored as a single file |
| Parameters | The numbers inside a model; "9B" means 9 billion of them |
| MoE (Mixture of Experts) | A model built from many parts ("experts") of which only a few are used per word; cheaper to run than its size suggests |
| A3B | Shorthand meaning "about 3 billion parameters active per word" in an MoE model |
| GGUF | The file format llama.cpp runs; what you download from HuggingFace |
| Quantization | Storing the model's numbers with less precision to make the file smaller; slightly less sharp, much easier to run |
| BF16 | Brain float 16: the usual full-precision (uncompressed) format; the biggest file in a quant ladder |
| Q4_K_M, Q5_K_M, IQ4_XS | Names of quantization levels; higher number means bigger file and better quality. But the exact file size depends on the model itself, not just the label; two different models at the same label can differ a lot in size |
| bpw | Bits per parameter: how many bits each number gets; roughly file size divided by parameter count. The exact number depends on the model architecture, so treat it as a rough guide, not a fixed value |
| Context | How much text the model can keep in mind at once (the conversation plus any files) |
| Token | A word piece; models read and write tokens, not letters. tok/s = tokens per second |
| RAM | Working memory; the model must fit here while running |
| Disk | Storage; where the model file lives between runs |
| llama-server | The free program that runs a model file and shows a chat page in your browser |
| Port | An "apartment number" for a web service on your machine (8080 is ours) |
| BEAST / BEASTX | The phylogenetics program the lab uses; its input is an XML file describing the model |
| XML | A text format with nested tags; BEAST model files are XML |
| Agent | An assistant that can act (read files, edit files, run commands), not just chat |
| AGENTS.md | A plain text file of standing rules at the top of a project folder; OpenCode reads it at the start of every session |
| OpenCode | The terminal agent program used in this guide |
| MCP | A standard way to give assistants extra tools; each tool set is an "MCP server" |
| Skill | A small instruction file the assistant loads when relevant |
| Plugin | An installable extension for OpenCode |
| Ponytail | The installed plugin that makes the agent work in "lazy senior developer" mode |
| HuggingFace | The website where model files are shared (GitHub for models) |
| Apache-2.0 / MIT | Licenses that mean "free to use, including for research" |
| API | The machine-to-machine way programs talk to each other |
| LiteLLM / proxy | A local switchboard program that fronts the lab's authorized cloud models |
| Consensus | A commercial (paid) literature-search product; litsearch exists to check whether such tools are needed at all |
| SearXNG | A self-hosted web search engine; no API keys, no rate limits |
| MCMC | Markov chain Monte Carlo: the math BEAST uses to fit a model to data |
| mmproj | A small extra file that gives a model image input |
| Draft file | A small companion file that makes a model answer faster; not a model by itself |
| eGPU | An external graphics card in a box, plugged into the laptop |
| Unified memory | Memory shared between processor and graphics (Mac laptops, Strix Halo mini-PCs); the model needs less of it |
| Strix Halo | AMD's chip for mini-PCs and laptops where CPU and GPU share one memory pool, 32-128GB |
| PubMed | The free government database of biomedical papers |
| PMC (PubMed Central) | The free full-text library for open-access papers |
| CyberTiel | One of the lab's local models (a 35B coding-focused one) |
| jsonc | A config file format: like JSON, but comments are allowed |
