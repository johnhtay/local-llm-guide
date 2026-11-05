# 03: Run the model

[llama.cpp](https://github.com/ggml-org/llama.cpp) is a free program that runs model
files. `llama-server` starts it as a small web service on your own computer, with a
chat page in your browser.

## Install llama-server

- **macOS:** `brew install llama.cpp`
- **Linux:** from the [releases page](https://github.com/ggml-org/llama.cpp/releases),
  download the latest `ubuntu-x64` zip, unzip it; you get a `llama-server` program.
- **Windows:** same releases page; pick the `cuda` zip if you have an NVIDIA GPU,
  otherwise the plain `cpu` zip.

## Run it

1. Put your `.gguf` file somewhere sensible, e.g. `~/models/`.
2. In a terminal:

```sh
llama-server -m ~/models/YOUR-MODEL-FILE.gguf -c 32768 --port 8080
```

3. Open `http://127.0.0.1:8080` in your browser. Chat away.
4. Stop with `Ctrl+C` in the terminal. Restart with the same command.

The first start takes a while (it loads the whole file into memory). After that,
answers start streaming immediately.

## If something goes wrong

| Message | Fix |
|---|---|
| out of memory | smaller model file (02), or lower the `-c` number |
| command not found | you are not in the folder with llama-server; use its full path |
| browser shows nothing | server still loading, or wrong port; check the terminal output |

## What the browser page offers

- A chat interface. The temperature slider is "creativity"; 0.7 to 0.9 is a good
  range for work. Leave the rest at defaults.
- This page is only for chatting. For an assistant that can read and edit your
  files, continue to [04-opencode.md](04-opencode.md).

---

*Unfamiliar words? One-line explanations in the [glossary](glossary.md).*
