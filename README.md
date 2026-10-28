# secret-leak-check

**Catch secrets before they ship.**

An agent skill for Claude Code, Cursor, and Codex. It checks what your app actually ships -- built assets and preview URLs -- for leaked secrets, exposed source maps, and publicly readable `.env`/`.git` files.

Most secret scanners read your git history. This one reads what goes live.

## Why

AI coding tools move fast. A key can end up in a client bundle, a preview URL is public by default, and a source map can rebuild your source. These are the things that are invisible until they are dangerous.

## Install

One `SKILL.md` works in all three tools.

| Tool | Install |
|---|---|
| Claude Code | `mkdir -p ~/.claude/skills && cp -r secret-leak-check ~/.claude/skills/` |
| Cursor | `mkdir -p ~/.cursor/skills && cp -r secret-leak-check ~/.cursor/skills/` |
| Codex | `mkdir -p ~/.codex/skills && cp -r secret-leak-check ~/.codex/skills/` |

Cursor also reads `~/.claude/skills/` and `~/.codex/skills/`, so a single Claude Code install is usually enough for both Cursor and Claude Code.

On Windows, run the commands in Git Bash, or copy the folder with PowerShell:

```powershell
Copy-Item -Recurse . "$HOME\.claude\skills\secret-leak-check"
```

## Use

Ask your agent:

> Check this preview URL before I deploy: https://example-preview.vercel.app

or:

> Scan ./dist for leaked secrets and source maps before I ship.

The skill runs the deterministic checks in `references/checks.md` and returns:

- FAIL -- do not deploy
- WARN -- deploy with fixes
- PASS -- clean

Secrets are reported by type and location, never printed in full.

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

## License

MIT
