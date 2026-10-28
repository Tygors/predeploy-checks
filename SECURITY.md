# Security Policy

## Supported versions

The latest release on `main` is supported. Older commits are handled on a best-effort basis.

## Reporting a vulnerability

Please do not open a public issue for a vulnerability in a skill itself.

Use GitHub's private vulnerability reporting:

https://github.com/Tygors/predeploy-checks/security/advisories/new

Include:

- the affected skill, version, or commit
- the agent and version (Claude Code, Cursor, or Codex)
- the target type (preview URL, build directory, or repository)
- the redacted output and a minimal reproduction
- the impact you expect

## Scope

In scope:

- command or instruction injection in a skill
- redaction failures that could expose a secret
- allowlist mistakes that hide a real secret
- instructions that cause unexpected file writes, network calls, data uploads, or code execution
- test commands that reach production services or install packages without the user's consent

Out of scope:

- a secret found in your application. That is a finding, not a vulnerability in this tool. Report it with the False positive or Missed secret issue template.
- secrets in git history. `secret-leak-check` scans shipped output, not history.
- a test audit, regression check, contract check, or preview check classification you disagree with. Use the corresponding feedback template.
- vulnerabilities in the project being audited. Report those to that project.

## Data handling

The skills are local-only. They have no telemetry and upload nothing. They should only read the target you name.

`test-audit`, `regression-check`, and `contract-check` run the project's existing test commands when available. Tests execute repository code and may use network, databases, or credentials. Run the audit only in a local checkout you trust, and review any test command before allowing it to run.

`preview-check` sends GET and HEAD requests only to the origin the user names and renders pages with local Chrome. It must not authenticate, submit forms, click through flows, or follow other origins.

## Never paste real secrets

Redact every key and token before posting an issue or advisory. Do not paste production data or personal data. If a real credential was exposed, rotate it first.

## Response

This is a volunteer project. Reports are handled on a best-effort basis. We will acknowledge a valid report and coordinate disclosure.
