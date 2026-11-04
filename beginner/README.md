# Your own AI assistant, fully offline (beginner version)

For anyone who knows a little Linux and a little R or Python, and nothing about AI
tooling. Total setup time: about an hour. Nothing leaves your computer: no account,
no API key, no internet needed after the one-time download.

## What you will set up

1. **A model file**: a big file you download once. This file *is* the assistant's brain.
2. **llama-server**: a small free program that runs the model and gives you a chat page
   in your browser.
3. **OpenCode** (optional, worth it): a terminal assistant that uses the same model but
   can also read and edit your files.

## The one-page decision table

| Your computer | What to run | Speed |
|---|---|---|
| Laptop with 16GB RAM | 9B model (~6GB file) | you can watch it type; fine for chat and code questions |
| Laptop with 32GB RAM | 35B "MoE" model (~15GB file) | noticeably faster |
| Mac with 32GB+ unified memory | same as 32GB laptop | faster again |
| eGPU dock or good GPU | same 35B model | fastest |

("MoE" models only use about 3 billion of their 35 billion numbers per word, so they
run surprisingly well on ordinary laptops. Explained in 02.)

## The files, in order

| File | What it teaches | Time |
|---|---|---|
| [01-huggingface.md](01-huggingface.md) | Where to download a model and which file to pick | 5 min |
| [02-hardware-fit.md](02-hardware-fit.md) | Will it run on my computer? | 5 min |
| [03-llamacpp-server.md](03-llamacpp-server.md) | Run the model, chat in the browser | 15 min |
| [04-opencode.md](04-opencode.md) | The assistant that can edit your files | 20 min |
| [05-models.md](05-models.md) | Which model, exactly | 5 min |

When this feels easy, the parent folder (`..`) has the full guide: quantization math,
multi-GPU setups, context tuning, and the agent extensions (MCP, skills, plugins).
