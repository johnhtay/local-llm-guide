# 04: OpenCode, the workhorse

OpenCode is a terminal program and the main tool this guide is built around. You
talk to it in plain English and it can:

- read the files in your project and explain them
- edit files, run commands, fix errors, write tests

By default it asks before doing anything risky, so nothing happens without your
approval. **But this only holds if you leave the permission settings alone.** If
you give OpenCode always-on permissions (for example, allowing file edits or
shell commands without confirmation), it will act without asking. This is a real
data-loss risk: with broad file-edit permissions, a single wrong command like
`rm *` can permanently delete every file in the current directory, and OpenCode
will run it without pausing. Treat permissions as the safety mechanism they are:
keep them on "ask" until you are sure you know what you are doing, and never
grant always-on file-edit permissions on a directory you care about without a
backup.

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
- "Here is the full error text: [paste it]. What went wrong and how do I fix it?"

When something breaks, paste the complete error message into your message. The
model can only work with what it can see: "fix the error above" invites a guess,
while the real error text points at the actual cause. If nothing printed an
error, describe what you did, what you expected, and what happened instead, in
as much detail as you can.

One habit worth stealing for your own projects: in a very long working session,
an assistant starts to forget what you told it at the beginning. Put standing
rules in a file named `AGENTS.md` at the top of your project folder; OpenCode
reads it at the start of every session, so the rules last longer than the
conversation. This guide's own repository has one.

## Two extras, for when you are curious

- **MCP**: add-on tools, e.g. searching PubMed or the web from inside OpenCode.
- **Skills**: ready-made instruction packs for specific tasks.

Both get their own plain-language chapter: [07-ecosystem.md](07-ecosystem.md).

## Pi: a lightweight alternative (stub)

[Pi](https://github.com/earendil-works/pi-coding-agent) is a smaller, lighter
assistant that does a subset of what OpenCode does. Its small size is both its
boon and its downfall: it is quick to install and start, but it lacks many of the
features that make OpenCode the workhorse here. I do not have enough measured
experience with Pi to say more yet, so this is a stub; treat OpenCode as the
default and Pi as something to watch.

---

*Unfamiliar words? One-line explanations in the [glossary](glossary.md).*
