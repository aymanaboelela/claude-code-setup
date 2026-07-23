# Skills Catalog

24 skills across three families. Each skill is a self-contained folder under
[`skills/`](../skills/) with a `SKILL.md` (and, where noted, bundled reference
docs, scripts, or assets).

**Invocation column:**
- **Auto** — Claude can invoke it on its own when the task matches.
- **Manual** — user-invoked only (`/skill-name`); the model won't auto-trigger it.

---

## 🔒 Mobile Security — OWASP MASVS / MASTG (13)

A full mobile app security toolkit built around the OWASP **MASVS v2** verification
standard and **MASTG** testing guide. Covers threat modeling, planning, per-domain
audits, and a scriptable Top-10 scanner.

| Skill | Invocation | What it does |
|-------|-----------|--------------|
| [`mobile-threat-model`](../skills/mobile-threat-model/) | Manual | STRIDE threat model mapped to MASVS controls — run at project start or before a security review. |
| [`mobile-pentest-plan`](../skills/mobile-pentest-plan/) | Manual | Penetration-testing plan from MASTG methodology + NowSecure practices (scope, checklist, engagement prep). |
| [`masvs-checklist`](../skills/masvs-checklist/) | Manual | Generates a MASVS v2 compliance checklist with MASTG test mappings and gap analysis. |
| [`owasp-mobile-security-checker`](../skills/owasp-mobile-security-checker/) | Auto | OWASP Mobile Top 10 (2024) audit. **Bundles Python scanners** for hardcoded secrets, dependencies, network config, and storage. |
| [`auth-assessment`](../skills/auth-assessment/) | Auto | MASVS-AUTH — login flows, biometrics, session management, MFA, access control. |
| [`crypto-review`](../skills/crypto-review/) | Auto | MASVS-CRYPTO — encryption, key management, hashing, RNG, protocol usage. |
| [`network-security-check`](../skills/network-security-check/) | Auto | MASVS-NETWORK — TLS config, certificate pinning, cleartext traffic. |
| [`platform-interaction-review`](../skills/platform-interaction-review/) | Auto | MASVS-PLATFORM — IPC, WebViews, deep links, URL schemes, permissions. |
| [`privacy-audit`](../skills/privacy-audit/) | Auto | MASVS-PRIVACY — data minimization, tracking, consent, transparency. |
| [`resilience-assessment`](../skills/resilience-assessment/) | Auto | MASVS-RESILIENCE — anti-tamper, root/jailbreak detection, obfuscation, anti-debug. |
| [`secure-storage-audit`](../skills/secure-storage-audit/) | Auto | MASVS-STORAGE — data-at-rest, local storage, data leakage. |
| [`code-quality-scan`](../skills/code-quality-scan/) | Auto | MASVS-CODE — vulnerable dependencies, input validation, injection, outdated platform reqs. |
| [`secure-mobile-dev-guide`](../skills/secure-mobile-dev-guide/) | Auto | Secure-by-design implementation guidance (NowSecure guide + MASVS + MASTG). |

**Bundled resources**
- `owasp-mobile-security-checker/scripts/` — `scan_hardcoded_secrets.py`, `check_dependencies.py`, `check_network_security.py`, `analyze_storage_security.py`
- `owasp-mobile-security-checker/references/owasp_mobile_top_10_2024.md`

---

## 📱 Flutter / Mobile Development (3)

| Skill | Invocation | What it does |
|-------|-----------|--------------|
| [`flutter-tester`](../skills/flutter-tester/) | Auto | Write/fix/review Flutter tests — unit, widget, integration, Riverpod, Mockito, GetIt, Given-When-Then patterns. Ships 3 reference guides. |
| [`dynamic-app-icon-splash`](../skills/dynamic-app-icon-splash/) | Auto | Swap a Flutter app's launcher icon + in-app splash for seasons/occasions (Ramadan, Eid, sales) via remote config — **no store update**. iOS alternate icons, Android activity-alias. |
| [`svg-draw-animation`](../skills/svg-draw-animation/) | Auto | Turn an SVG/logo into a Flutter "self-drawing" animation for splash screens and branded loaders. Bundles inspection scripts + a Dart animation asset. |

---

## ⚙️ Workflow & Process (8)

| Skill | Invocation | What it does |
|-------|-----------|--------------|
| [`tdd`](../skills/tdd/) | Auto | Test-driven development — red-green-refactor loop. Ships references on deep modules, interface design, mocking, refactoring, and tests. |
| [`write-a-skill`](../skills/write-a-skill/) | Auto | Author new skills with proper structure, progressive disclosure, and bundled resources. |
| [`handoff`](../skills/handoff/) | Auto | Compact the current conversation into a handoff document for the next session/agent. |
| [`grill-with-docs`](../skills/grill-with-docs/) | Auto | Stress-test a plan against the domain model, sharpen terminology, and update CONTEXT.md / ADRs inline. |
| [`to-prd`](../skills/to-prd/) | Auto | Turn the current conversation into a PRD and publish it to the issue tracker. |
| [`to-issues`](../skills/to-issues/) | Auto | Break a plan/spec/PRD into independently-grabbable, tracer-bullet issues. |
| [`teach`](../skills/teach/) | Manual | Teach a new concept or skill within the workspace, tracking a learning record. |
| [`caveman`](../skills/caveman/) | Auto | Ultra-compressed communication mode — ~75% fewer tokens, full technical accuracy. |

---

## Attribution

Skill folders are preserved verbatim, including any original `author` / `version`
metadata in their frontmatter (e.g. `flutter-tester` and
`owasp-mobile-security-checker` credit their original author). Several
workflow/security skills are adapted from the wider Claude Code and
[Superpowers](https://github.com/anthropics/claude-plugins-official) community.
This repository is a personal, restorable collection — credit stays with the
original authors where their metadata is present.
