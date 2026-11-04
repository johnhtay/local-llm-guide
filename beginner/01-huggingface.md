# 01: Where to get a model (HuggingFace)

[HuggingFace](https://huggingface.co) is GitHub for AI models. Labs upload their
models; anyone can download. You need exactly one skill here: picking the right file.

## What you download

One file whose name ends in `.gguf`. That is a "compressed" copy of the model:
smaller file, slightly less sharp, much easier to run. Think MP3 instead of WAV.

The file name tells you the compression level. The everyday choice is
`Q4_K_M`; a bit smaller is `IQ4_XS`; anything below `Q3` starts to lose noticeably.
(More detail than you need right now is in the advanced guide, file 01.)

## How to actually get it

1. Pick your model from [05-models.md](05-models.md).
2. On huggingface.co, search that model name.
3. Open the **Files and versions** tab.
4. Download the `.gguf` file whose size fits your RAM (next chapter).
5. A plain browser download is fine. Put it in a folder like `~/models/`.

**License check** (on the model's front page): Apache-2.0 or MIT means free to use,
including for research. Anything else, read the terms.

## Ignore, for now

- `.safetensors` files: the original uncompressed weights. Not what llama.cpp runs.
- Files with `-draft` in the name: speed-up helpers, not standalone models.
- Files with `mmproj` in the name: for image input (grab it later if you want images).
