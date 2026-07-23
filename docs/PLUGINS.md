# Plugins & Marketplaces

The Claude Code plugins enabled on this setup, and the marketplaces they come
from. Plugins bundle their own skills, commands, agents, and MCP servers — so
restoring them brings back a large chunk of the environment on its own.

## Marketplaces

Add these first; plugins install from them.

| Marketplace | Source |
|-------------|--------|
| `claude-plugins-official` | `anthropics/claude-plugins-official` (built-in) |
| `cloudflare` | `cloudflare/skills` |

```bash
# The official marketplace is built in. Add the Cloudflare one:
claude plugin marketplace add cloudflare/skills
```

## Plugins

| Plugin | Marketplace | Purpose |
|--------|-------------|---------|
| `superpowers` | official | Workflow skills — brainstorming, planning, TDD, debugging, worktrees, code review. |
| `frontend-design` | official | Distinctive, intentional UI/visual design guidance. |
| `code-review` | official | Structured pull-request code review. |
| `code-simplifier` | official | Refactors recent changes for clarity without changing behavior. |
| `context7` | official | Live library/framework documentation (also an MCP server). |
| `github` | official | GitHub platform integration (MCP). |
| `security-guidance` | official | OWASP / MASVS mobile security guidance and scanners. |
| `figma` | official | Figma design-to-code, Code Connect, motion. |
| `stripe` | official | Stripe integration, best practices, error explainer. |
| `vercel` | official | Vercel deploy, AI SDK, Next.js, storage, CI/CD. |
| `firebase` | official | Firebase integration. |
| `chrome-devtools-mcp` | official | Browser automation, performance tracing, Lighthouse. |
| `cloudflare` | cloudflare | Workers, Pages, KV/D1/R2, Agents SDK, Wrangler. |

## Restore

```bash
claude plugin install superpowers@claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install code-review@claude-plugins-official
claude plugin install code-simplifier@claude-plugins-official
claude plugin install context7@claude-plugins-official
claude plugin install github@claude-plugins-official
claude plugin install security-guidance@claude-plugins-official
claude plugin install figma@claude-plugins-official
claude plugin install stripe@claude-plugins-official
claude plugin install vercel@claude-plugins-official
claude plugin install firebase@claude-plugins-official
claude plugin install chrome-devtools-mcp@claude-plugins-official
claude plugin install cloudflare@cloudflare
```

> The exact enabled set is also captured in
> [`config/settings.template.json`](../config/settings.template.json) under
> `enabledPlugins`.
