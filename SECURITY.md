# Security Policy

## Supported versions

The latest release on `main` is supported. Older commits are handled on a best-effort basis.

## Reporting a vulnerability

Please do not open a public issue for a vulnerability in the skill itself.

Use GitHub's private vulnerability reporting:

https://github.com/Tygors/secret-leak-check/security/advisories/new

Include:

- the affected version or commit
- the agent and version (Claude Code, Cursor, or Codex)
- the target type (preview URL or build directory)
- the redacted output and a minimal reproduction
- the impact you expect

## Scope

In scope:

- command or instruction injection in the skill
- redaction failures that could expose a secret
- allowlist mistakes that hide a real secret
- unexpected file writes, network calls, or data uploads

Out of scope:

- a secret found in your application. That is a finding, not a vulnerability in this tool. Report it with the False positive or Missed secret issue template.
- secrets in git history. This skill scans shipped output, not history.

## Data handling

The skill is local-only. It has no telemetry and uploads nothing. It should only read the target you name.

## Never paste real secrets

Redact every key and token before posting an issue or advisory. If a real credential was exposed, rotate it first.

## Response

This is a volunteer project. Reports are handled on a best-effort basis. We will acknowledge a valid report and coordinate disclosure.
