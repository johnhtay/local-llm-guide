# 07: Extra abilities: tools, recipes, and good habits

The model answers questions. These three additions make it *do* things.

## MCP: giving the assistant tools

- MCP is a standard way to plug extra tools into an assistant. Each set of tools is
  a small program called an "MCP server".
- The two that matter here:
  - **PubMed**: twelve research tools. Search PubMed, fetch full papers through
    open-access sources, format citations, find related papers, get citation
    metrics. You ask in plain English: "find papers on dengue molecular clocks
    from the last two years and pull the open-access ones".
  - **Web search**: a search tool with no API keys. Ours prefers our own
    self-hosted search engine (SearXNG) and falls back to public ones.
- Where to find more: the
  [Awesome MCP Servers list](https://github.com/punkpeye/awesome-mcp-servers)
  catalogs hundreds of servers, sorted by category. New publication and research
  tools appear weekly.

## Skills: ready-made instruction packs

- A skill is a small instruction file the assistant loads only when it becomes
  relevant. It turns a general model into a specialist for one task.
- The lab's set includes: writing and checking BEAST model files (several skills),
  making publication figures, and manuscript style for the group's target
  journals.
- Writing your own is one markdown file with a one-line description.

## Plugins: extensions

Two are installed here:

- **agent-memory**: the assistant keeps notes between sessions, so it remembers
  decisions, paths, and gotchas instead of starting from zero every time.
- **Ponytail** (deserves its own mention): it turns the assistant into a "lazy
  senior developer". The smallest change that fully works, no features nobody
  asked for, and every reply must end with what it did not check. For lab code,
  that closing statement is exactly the honesty you want.

## One window instead of a terminal

- OpenCode lives in the terminal. If you would rather click than type,
  [AIPOCH Open-Science](https://github.com/aipoch/open-science) is a free,
  open-source desktop application (macOS, Windows, and Linux) that puts the
  same ideas in a window: chat, files, and tools in panels instead of
  commands.
- It connects to the same llama-server from [03](03-llamacpp-server.md), so the
  model you already run works unchanged. This guide keeps the pieces separate
  so you can see each one work; AIPOCH bundles them into one app.

![The AIPOCH Open-Science desktop workbench (screenshot: github.com/aipoch/open-science)](../charts/aipoch-workspace.png)

Full detail: [../07-ecosystem.md](../07-ecosystem.md) in the advanced track.

---

*Unfamiliar words? One-line explanations in the [glossary](glossary.md).*
