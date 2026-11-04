# 04: OpenCode: the agent on top

[OpenCode](https://opencode.ai) is a terminal coding agent: it reads your repo, edits
files, runs tools, and answers, with **any** OpenAI-compatible model behind it,
including the local `llama-server` from [03](03-llamacpp-server.md). The same guide
shows how to extend it with MCP tools, skills, and plugins, and let local and cloud models live
side by side.

## Install and first run

```sh
curl -fsSL https://opencode.ai/v2/install | bash   # or: npm i -g @opencode/cli
opencode                                            # TUI in your project dir
```

OpenCode runs a background service (sessions, tools, permissions live there);
check it with `opencode service status`. No API key needed for a local server.

## Point it at your local server

Configuration lives in `~/.config/opencode/opencode.jsonc` (global) and/or
`.opencode/opencode.jsonc` (project). Real example: the 9B provider, verbatim from
the lead tester's config (URL uses `127.0.0.1` when both run on the same machine;
a WSL↔Windows split uses the host gateway IP instead):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "qwen-local-9b/qwen3.8-9b",          // format: provider/model-id
  "small_model": "qwen-local-9b/qwen3.8-9b",    // cheap tasks: titles, summaries
  "providers": {
    "qwen-local-9b": {
      "package": "@opencode/ai/providers/openai-compatible",
      "name": "Qwen3.8-9B (llama.cpp)",
      "settings": { "baseURL": "http://127.0.0.1:9932/v1" },
      "models": {
        "qwen3.8-9b": {
          "name": "Qwen3.8-9B (local)",
          "limit": { "context": 131072, "output": 16384 },
          "body": { "temperature": 0.85 }
        }
      }
    }
  }
}
```

Two details that matter:

- **`limit.context` must match the server's `-c`** (or be lower), the agent plans
  around it.
- **Config edits hot-reload**, no restart needed; `/reload` forces a full one.
  Declare what the model can actually do (`capabilities.input: ["text"]` vs
  `["text","image"]`) or you'll chase 400 errors on image paste.

## MCP: give the agent tools

MCP servers add tools (search, PubMed, databases…). Remote servers are one command:

```sh
opencode mcp add <name> --global --url <https://server-url>
opencode mcp list
```

Local (command-based) servers are a JSONC entry, real example, the PubMed server
(twelve research tools; note it requires Node ≥ 24):

```jsonc
"mcp": {
  "servers": {
    "pubmed": {
      "type": "local",
      "command": [
        "~/.nvm/versions/node/v24/bin/node",
        "~/.nvm/versions/node/v24/lib/node_modules/@cyanheads/pubmed-mcp-server/dist/index.js"
      ]
    }
  }
}
```

Note the layering: [03](03-llamacpp-server.md) gave the *server* its own MCP tools
(used by llama-server's web UI); OpenCode's MCP is client-side and used by the agent.
Both can run simultaneously.

## Skills: reusable playbooks

A skill is a `SKILL.md` the model loads on demand when relevant, instructions plus
supporting files, without bloating every prompt.

```text
.opencode/skills/        ← project skills (or ~/.config/opencode/skills for global)
└── beastx-xml/
    └── SKILL.md         ← frontmatter: name + one-line "when to use" description
```

Load manually by mentioning `@beastx-xml` in a prompt. Built-ins load automatically,
the lead tester's daily set includes `ponytail` (concise dev mode), `beastx-xml`,
`beastx-mmm` (BEASTX model configs), `d3-diagrams`, `pubmed` workflow helpers.

## Plugins: extend the agent itself

Plugins are npm packages that hook sessions, transform tool calls, or add TUI
elements. Config (canonical V2 field):

```jsonc
"plugins": ["opencode-agent-memory", "@dietrichgebert/ponytail"]
```

The lead tester runs an agent-memory plugin (persistent notes across sessions) and
ponytail (minimal-change coding mode). Writing your own is documented at
[opencode.ai/v2/docs/build/plugins](https://opencode.ai/v2/docs/build/plugins).

## Permissions: gate what the agent may do

```jsonc
"permissions": [
  { "action": "external_directory", "resource": "*", "effect": "ask" }
]
```

Effects: `allow` / `ask` / `deny`, last matching rule wins. Start with `ask`
everywhere and relax as trust grows.

## Long sessions: compaction

Long sessions auto-compact (summarized and continued). One knob worth knowing:

```jsonc
"compaction": { "buffer": "25%" }
```

The default can squeeze the summary too hard on local models; 25% gives them room.

## LiteLLM: local + cloud side by side

A local [LiteLLM](https://docs.litellm.ai/) proxy (127.0.0.1:4000) fronts authorized
cloud endpoints behind one key, so OpenCode treats them like another provider:

```jsonc
"litellm": {
  "package": "@opencode/ai/providers/openai-compatible",
  "name": "Lab proxy",
  "settings": { "baseURL": "http://127.0.0.1:4000/v1", "apiKey": "sk-<your-virtual-key>" },
  "models": {
    "big":    { "limit": { "context": 262144, "output": 32768 },
                "capabilities": { "tools": true, "input": ["text"], "output": ["text"] } }
  }
}
```

Now `Tab` in the TUI switches between e.g. `qwen-local-9b/qwen3.8-9b` and
`litellm/big`. Keep credentials in the proxy's env file, never in `opencode.jsonc`;
one diagnostic gotcha: `/v1/models` answers even with a bad key: test auth with
`/v1/chat/completions` instead.
