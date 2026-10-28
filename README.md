# secret-leak-check

**Catch secrets before they ship.**

An agent skill for Claude Code, Cursor, and Codex. It checks what your app actually ships -- built assets and preview URLs -- for leaked secrets, exposed source maps, and publicly readable `.env`/`.git` files.

Most secret scanners read your git history. This one reads what goes live.

**No telemetry. No uploads. Local-only.**

![Local build scan](https://github.com/Tygors/secret-leak-check/releases/download/v0.1.0/secret-leak-check-local.gif)

*Local build scan. Recorded from a real Claude Code session; output condensed.*

## Why

AI coding tools move fast. A key can end up in a client bundle, a preview URL is public by default, and a source map can rebuild your source. These are the things that are invisible until they are dangerous.

### How it compares

| | secret-leak-check | gitleaks / detect-secrets |
|---|---|---|
| Scans | built assets and preview URLs | git history and repository files |
| Source maps | yes, including `sourcesContent` | no |
| Runs as | Claude Code / Cursor / Codex skill | standalone binary |
| Best for | pre-deploy gate | commit-time scanning |

## Install

One `SKILL.md` works in all three tools.

| Tool | Install |
|---|---|
| Claude Code | `mkdir -p ~/.claude/skills && cp -r skills/secret-leak-check ~/.claude/skills/` |
| Cursor | `mkdir -p ~/.cursor/skills && cp -r skills/secret-leak-check ~/.cursor/skills/` |
| Codex | `mkdir -p ~/.codex/skills && cp -r skills/secret-leak-check ~/.codex/skills/` |

The skill lives in `skills/secret-leak-check/`; `examples/` is only the demo fixture and is not installed.

Cursor also reads `~/.claude/skills/` and `~/.codex/skills/`, so a single Claude Code install is usually enough for both Cursor and Claude Code.

On Windows, run the commands in Git Bash, or copy the folder with PowerShell:

```powershell
Copy-Item -Recurse .\skills\secret-leak-check "$HOME\.claude\skills\secret-leak-check"
```

## Use

Ask your agent:

> Check this preview URL before I deploy: https://example-preview.vercel.app

or:

> Scan ./dist for leaked secrets and source maps before I ship.

The skill runs the deterministic checks in `skills/secret-leak-check/references/checks.md` and returns:

- FAIL -- do not deploy
- WARN -- deploy with fixes
- PASS -- clean

Secrets are reported by type and location, never printed in full.

## Demo

The local build scan is above. For the preview URL scan and the safe fixture, see [examples/vulnerable](examples/vulnerable/README.md); the fixture is generated with `python examples/vulnerable/make_demo.py`.

## What it checks

1. Known API key and token formats in shipped HTML/JS/JSON.
2. JWTs with `role: service_role` in client assets.
3. Publicly reachable source maps, including `sourcesContent` and inline maps.
4. Publicly readable `.env`, `.git/config`, and `.DS_Store`.

## What it does not do

- It does not scan git history. Use `gitleaks` or `detect-secrets` for that.
- It does not use entropy scanning; false positives are worse than missing a generic string.
- It does not upload or store anything.
- It is not a full security audit.

If this catches one leak before it ships, a star helps someone else find it.

## Contributing

Reports of false positives and missed patterns are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the issue templates.

## License

MIT
