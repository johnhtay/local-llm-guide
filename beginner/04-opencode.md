# 04: OpenCode, the assistant that can edit your files (optional, worth it)

OpenCode is a terminal program. You talk to it in plain English and it can:

- read the files in your project and explain them
- edit files, run commands, fix errors, write tests

It always asks before doing anything risky, so nothing happens without your approval.
It uses the same model you are already running from [03](03-llamacpp-server.md).

## Install

Linux and macOS:

```sh
curl -fsSL https://opencode.ai/v2/install | bash
```

Windows: install WSL first (Windows Subsystem for Linux), then the command above
inside WSL.

## Point it at your local model

Create a file `~/.config/opencode/opencode.jsonc` with exactly this content (adjust
the model file name to yours):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "local/my-model",
  "providers": {
    "local": {
      "package": "@opencode/ai/providers/openai-compatible",
      "name": "My local model",
      "settings": { "baseURL": "http://127.0.0.1:8080/v1" },
      "models": {
        "my-model": {
          "name": "My local model"
        }
      }
    }
  }
}
```

Note the `/v1` at the end of the URL: it must be there. Port 8080 matches the
command in [03](03-llamacpp-server.md).

## Use it

Keep llama-server running (chapter 03), then:

```sh
cd my-project
opencode
```

Try these prompts:

- "Explain what this repository does."
- "Find everywhere the variable X is used."
- "Write a test for the function Y."
- "Fix the error in the output above."

## Two extras, for when you are curious

- **MCP**: add-on tools, e.g. searching PubMed or the web from inside OpenCode.
- **Skills**: ready-made instruction packs for specific tasks.

Both are optional and take five minutes each; the advanced guide (parent folder,
file 04) covers them when you want more.
