# Claude Code Setup

> A portable, restorable [Claude Code](https://claude.ai/code) environment — **24 skills**, the MCP connections that power them, the plugin set, and a sanitized config template. Clone it onto any machine (or a brand-new account) and get the same setup back in a couple of minutes.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-24-brightgreen)
![Platform](https://img.shields.io/badge/Claude%20Code-macOS%20%7C%20Linux%20%7C%20Windows-5A67D8)

---

## Why this exists

Claude Code skills, MCP connections, plugins, and settings normally live only in
your local `~/.claude` folder. Reinstall your machine, switch accounts, or set up
a second workstation and it's all gone. This repo is the backup: everything needed
to reconstruct the environment, version-controlled and documented so **anyone**
looking at it understands what each piece does.

It contains three things:

1. **Skills** — 24 ready-to-use agent skills (mobile security, Flutter, workflow).
2. **Connections & plugins** — documented lists of every MCP server and plugin, with re-add commands.
3. **Config** — a sanitized `settings.json` template (no secrets) to drop in and personalize.

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

---

## What's inside

### Skills → [`docs/SKILLS.md`](docs/SKILLS.md)

| Family | Count | Highlights |
|--------|:-----:|------------|
| 🔒 **Mobile Security** (OWASP MASVS / MASTG) | 13 | Threat modeling, pentest planning, MASVS checklist, a scriptable Top-10 scanner, and per-domain audits (auth, crypto, network, storage, privacy, platform, resilience, code). |
| 📱 **Flutter / Mobile Dev** | 3 | Flutter test authoring, remote-config seasonal app icons + splash, and self-drawing SVG logo animations. |
| ⚙️ **Workflow & Process** | 8 | TDD loop, skill authoring, session handoff, plan-grilling, PRD/issue generation, teaching, and a token-saving "caveman" mode. |

### Connections → [`docs/CONNECTIONS.md`](docs/CONNECTIONS.md)

MCP servers that were wired up — `github`, `dart`, `supabase`, `context7`,
`figma`, `talk-to-figma`, `ffmpeg-montage` — each with a copy-paste re-add command.
**No credentials are stored here**; you supply your own at connect time.

### Plugins → [`docs/PLUGINS.md`](docs/PLUGINS.md)

13 plugins from the official `claude-plugins-official` marketplace and
`cloudflare/skills` (superpowers, frontend-design, code-review, github, figma,
vercel, stripe, firebase, cloudflare, and more), with one-line install commands.

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
│   └── PLUGINS.md                ← plugins + marketplaces + install commands
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
5. Reconnect MCP servers you use — [`docs/CONNECTIONS.md`](docs/CONNECTIONS.md).
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
