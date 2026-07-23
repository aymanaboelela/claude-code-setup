<p align="center">
  <img src="docs/assets/banner.svg" alt="Claude Code Setup — back up your skills, connections & config; restore any machine in minutes" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-6366f1.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/skills-24-a855f7" alt="24 skills">
  <img src="https://img.shields.io/badge/MCP%20connections-7-22d3ee" alt="7 MCP connections">
  <img src="https://img.shields.io/badge/Claude%20Code-macOS%20·%20Linux%20·%20Windows-38bdf8" alt="Platform">
  <img src="https://img.shields.io/github/last-commit/aymanaboelela/claude-code-setup?color=27c93f" alt="Last commit">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs welcome">
</p>

<p align="center">
  <b>A portable, restorable <a href="https://claude.ai/code">Claude Code</a> environment.</b><br>
  24 agent skills · the MCP connections that power them · the plugin set · a sanitized config template.<br>
  Clone it onto any machine — or a brand-new account — and get the same setup back in a couple of minutes.
</p>

---

## Why this exists

Claude Code skills, MCP connections, plugins, and settings normally live only in
your local `~/.claude` folder. Reinstall your machine, switch accounts, or set up
a second workstation and it's all gone. **This repo is the backup** — everything
needed to reconstruct the environment, version-controlled and documented so
anyone can understand what each piece does.

```mermaid
flowchart LR
    R(("Claude Code<br/>Setup")):::root
    R --> S["🔒 Mobile Security<br/><b>13 skills</b>"]:::sec
    R --> F["📱 Flutter<br/><b>3 skills</b>"]:::flu
    R --> W["⚙️ Workflow<br/><b>8 skills</b>"]:::wf
    R --> C["🔌 MCP connections<br/><b>7 servers</b>"]:::mcp
    R --> P["🧩 Plugins<br/><b>13 + 2 marketplaces</b>"]:::plg
    R --> G["⚙️ Config template<br/><b>no secrets</b>"]:::cfg

    classDef root fill:#6d28d9,stroke:#a855f7,color:#fff,stroke-width:2px;
    classDef sec fill:#3b1230,stroke:#f472b6,color:#ffd9ec;
    classDef flu fill:#0b2942,stroke:#38bdf8,color:#d6f2ff;
    classDef wf  fill:#241748,stroke:#a78bfa,color:#e9defc;
    classDef mcp fill:#08303a,stroke:#22d3ee,color:#d0fbff;
    classDef plg fill:#1a1f42,stroke:#818cf8,color:#e0e4ff;
    classDef cfg fill:#14213a,stroke:#64748b,color:#dbe4f0;
```

---

## Quick start

```bash
git clone https://github.com/aymanaboelela/claude-code-setup.git
cd claude-code-setup
./install.sh
```

That copies every skill into `~/.claude/skills/`. Then finish the environment:

```bash
# 1. Config — copy the template and add your own token
cp config/settings.template.json ~/.claude/settings.json

# 2. Plugins — see docs/PLUGINS.md
# 3. MCP connections — see docs/CONNECTIONS.md
```

`./install.sh --force` overwrites existing skills of the same name;
`./install.sh --link` symlinks them so edits sync back into this repo.

### The full restore, at a glance

```mermaid
flowchart LR
    A["📥 git clone"] --> B["⚡ ./install.sh<br/>skills → ~/.claude"]
    B --> C["⚙️ settings.template.json<br/>→ settings.json"]
    C --> D["🧩 install plugins<br/>PLUGINS.md"]
    D --> E["🔌 reconnect MCP<br/>CONNECTIONS.md"]
    E --> F(("✅ Ready")):::done
    classDef done fill:#0f3d24,stroke:#27c93f,color:#c7ffd8,stroke-width:2px;
```

---

## What's inside

### 🧠 Skills → [`docs/SKILLS.md`](docs/SKILLS.md)

| Family | Count | Highlights |
|--------|:-----:|------------|
| 🔒 **Mobile Security** (OWASP MASVS / MASTG) | 13 | Threat modeling, pentest planning, MASVS checklist, a scriptable Top-10 scanner, and per-domain audits (auth, crypto, network, storage, privacy, platform, resilience, code). |
| 📱 **Flutter / Mobile Dev** | 3 | Flutter test authoring, remote-config seasonal app icons + splash, and self-drawing SVG logo animations. |
| ⚙️ **Workflow & Process** | 8 | TDD loop, skill authoring, session handoff, plan-grilling, PRD/issue generation, teaching, and a token-saving "caveman" mode. |

### 🔌 Connections → [`docs/CONNECTIONS.md`](docs/CONNECTIONS.md)

The MCP servers that were wired up — each with a copy-paste re-add command.
**No credentials are stored here**; you supply your own at connect time.

```mermaid
flowchart TB
    CC(("Claude Code")):::hub
    CC --- GH["github<br/><i>repos · issues · PRs</i>"]:::n
    CC --- DA["dart<br/><i>Flutter tooling</i>"]:::n
    CC --- SB["supabase<br/><i>DB · migrations</i>"]:::n
    CC --- C7["context7<br/><i>live docs</i>"]:::n
    CC --- FG["figma<br/><i>Dev Mode</i>"]:::n
    CC --- TF["talk-to-figma<br/><i>edit designs</i>"]:::n
    CC --- FF["ffmpeg-montage<br/><i>video/audio</i>"]:::n

    classDef hub fill:#6d28d9,stroke:#22d3ee,color:#fff,stroke-width:2px;
    classDef n fill:#131c38,stroke:#5566b8,color:#dfe4fa;
```

### 🧩 Plugins → [`docs/PLUGINS.md`](docs/PLUGINS.md)

13 plugins from the official `claude-plugins-official` marketplace and
`cloudflare/skills` (superpowers, frontend-design, code-review, github, figma,
vercel, stripe, firebase, cloudflare, and more), each with a one-line install
command.

---

## Repository structure

```
claude-code-setup/
├── README.md                     ← you are here
├── install.sh                    ← restore skills into ~/.claude/skills
├── LICENSE                       ← MIT
├── config/
│   └── settings.template.json    ← sanitized settings (no secrets)
├── docs/
│   ├── SKILLS.md                 ← full catalog of all 24 skills
│   ├── CONNECTIONS.md            ← MCP servers + re-add commands
│   ├── PLUGINS.md                ← plugins + marketplaces + install commands
│   └── assets/
│       └── banner.svg            ← the header art
└── skills/                       ← the 24 skill folders (SKILL.md each)
    ├── auth-assessment/
    ├── caveman/
    └── … (22 more)
```

---

## Full restore checklist (fresh machine)

1. Install Claude Code and sign in.
2. `git clone` this repo and run `./install.sh`.
3. `cp config/settings.template.json ~/.claude/settings.json` and replace `CLAUDE_CODE_OAUTH_TOKEN` with your own.
4. Add marketplaces and install plugins — [`docs/PLUGINS.md`](docs/PLUGINS.md).
5. Reconnect the MCP servers you use — [`docs/CONNECTIONS.md`](docs/CONNECTIONS.md).
6. Restart Claude Code. Run `/` to confirm the skills are listed.

---

## Security

- **No secrets are committed.** Tokens, API keys, and OAuth credentials are
  excluded by design; `settings.json`, `.claude.json`, and `.env` are
  git-ignored, and the config here is a placeholder template.
- The security skills bundle **example** insecure snippets (e.g. a fake
  `sk_live_…` key) purely as "what not to do" documentation — those are not real
  credentials.
- Found something that looks like it shouldn't be public? Open an issue.

---

## Contributing

Branches follow a simple flow: `main` is stable, `develop` is the integration
branch, and changes land through pull requests. To add or update a skill, branch
off `develop`, drop the skill folder under `skills/`, update
[`docs/SKILLS.md`](docs/SKILLS.md), and open a PR.

---

## License

[MIT](LICENSE) — see [`docs/SKILLS.md`](docs/SKILLS.md#attribution) for attribution
of third-party skills, whose original author metadata is preserved in their
frontmatter.
