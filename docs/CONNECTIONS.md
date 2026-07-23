# MCP Connections

The MCP (Model Context Protocol) servers that were connected to this Claude Code
setup, and how to re-add them on a fresh machine.

> **No credentials live in this repo.** Tokens, keys, and access secrets are
> intentionally omitted. Each server below documents *what* it is and *how* to
> reconnect it — you supply your own credentials at connect time.

Add a server with the CLI:

```bash
# stdio (local process)
claude mcp add <name> -- <command> [args...]

# http / sse (remote endpoint)
claude mcp add --transport http <name> <url>
```

List / remove:

```bash
claude mcp list
claude mcp remove <name>
```

---

## User-scoped servers

| Name | Transport | What it does |
|------|-----------|--------------|
| `github` | http | GitHub's hosted MCP — repos, issues, PRs, code search, releases. |
| `dart` | stdio | Dart & Flutter tooling — analyze, format, run tests, hot reload, widget tree, device control. |
| `supabase` | stdio | Supabase project management — tables, migrations, SQL, edge functions, logs. |
| `context7` | stdio | Live, version-accurate library/framework documentation lookup. |
| `figma` | http | Figma **Dev Mode** local server (runs inside the Figma desktop app). |
| `talk-to-figma` | stdio | Bridge that lets the agent read/edit a live Figma document. |
| `ffmpeg-montage` | stdio | Local ffmpeg helper — trim, concat, montage, thumbnails, audio. |

### Re-add commands

```bash
# GitHub (hosted) — authenticate with your own GitHub token when prompted
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# Dart / Flutter — ships with the Dart SDK
claude mcp add dart -- dart mcp-server

# Supabase — supply your own access token via env at connect time
claude mcp add supabase -- npx -y @supabase/mcp-server-supabase@latest

# Context7 (also available as a plugin — see docs/PLUGINS.md)
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest

# Figma Dev Mode — start the local server from the Figma desktop app first,
# then point Claude Code at it
claude mcp add --transport http figma http://127.0.0.1:3845/mcp
```

> `ffmpeg-montage` and `talk-to-figma` were locally-hosted helper servers
> (run via `uv` and `node` respectively). Re-add them only if you still have the
> local server scripts; otherwise they are optional.

---

## Project-scoped servers

Some repositories carried their own MCP servers (stored in that project's
`.mcp.json`, not globally). Observed on this setup:

- `figma-desktop`
- `talk-to-figma`
- `tln-api`

These live inside their respective project repos and travel with them — they are
listed here only so nothing is a surprise when you open those projects again.
