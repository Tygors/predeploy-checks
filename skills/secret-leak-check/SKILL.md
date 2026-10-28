---
name: secret-leak-check
description: Check what an app actually ships to the browser for leaked secrets, exposed source maps, and publicly readable sensitive files. Use before deploying, after a preview deploy, or when the user asks whether a build or preview URL is safe to ship.
---

# Secret Leak Check

Scan the deployable output, not the git history. The goal is to catch secrets and source code that become public the moment the site goes live.

## When to use

- The user is about to deploy, publish, or go live.
- The user gives a preview or production URL and asks whether it is safe.
- The user asks to check a build directory (`dist/`, `build/`, `out/`, `.next/`, `public/`) for leaked keys, `.env` files, or source maps.

## Rules

- Use only the checks and patterns in `references/checks.md`. Do not invent new secret patterns.
- Never print a full secret. Redact matches before reporting.
- Read-only by default. Edit files or rotate keys only after the user asks.
- Scan only the host or directory the user names. Do not crawl other domains.
- Do not upload scan results anywhere.
- Any red finding means the current output should not be deployed.

## Step 1: Identify the target

- If the user gives a URL, scan the live output.
- If the user gives a source directory, ask which build output is deployed. Do not scan `node_modules`.

## Step 2: Scan a directory

Use your file-search tool (Grep) over the build output. Do not read whole bundles into context.

1. Find the secret formats in `references/checks.md`.
2. Find `*.map` files and `sourceMappingURL=` references.
3. Find `.env*`, `.git/config`, and `.DS_Store` inside the output.
4. For each JWT in client assets, decode the payload and check the `role` claim.

Redact before showing any match:

```bash
grep -nE '<pattern>' <file> \
  | sed -E 's/([A-Za-z0-9_-]{4})[A-Za-z0-9_-]{8,}([A-Za-z0-9_-]{4})/\1...\2/g'
```

## Step 3: Scan a URL

Use the terminal. On macOS, Linux, and Windows Git Bash:

```bash
ORIGIN="$(printf '%s' "$URL" | sed -E 's#(https?://[^/]+).*#\1#')"
tmp="$(mktemp -d)"
curl -fsSL --max-time 20 "$URL" -o "$tmp/index.html"

# Same-origin script URLs, at most 20.
grep -oE '<script[^>]+src="[^"]+"' "$tmp/index.html" \
  | sed -E 's/.*src="([^"]+)".*/\1/' > "$tmp/scripts.txt"
```

Download each script (maximum 20, 5 MB each, 15 second timeout). Skip cross-origin scripts. Then search with the patterns and redaction step from `references/checks.md`.

Check source maps:

```bash
grep -oE 'sourceMappingURL=[^[:space:]]+' "$tmp"/*.js
```

- If the map is reachable and contains `sourcesContent`, report a red finding.
- If `sourceMappingURL` is a `data:` URL, report a red finding.

Check sensitive files (same host only):

```bash
for p in .env .env.local .env.production .git/config .git/HEAD .DS_Store; do
  code="$(curl -s -o "$tmp/probe" -w '%{http_code}' --max-time 10 "$ORIGIN/$p")"
  printf '%s %s\n' "$code" "$p"
done
```

A probe is a finding only if the status is 200 and the body matches the file type. Ignore SPA HTML fallbacks.

On Windows PowerShell without Git Bash, use `curl.exe` and `Select-String`; the same checks apply.

## Step 4: Report

Always use this shape:

```text
FAIL - <summary>
  - <type> at <file>:<line> - <redacted evidence>
  - Fix: <one action>

WARN - <summary>
  - <path> - <why it matters>

PASS - <what was verified>
```

End with exactly one verdict line:

- `Verdict: DO NOT DEPLOY` if there is any red finding.
- `Verdict: DEPLOY WITH FIXES` if there are only warnings.
- `Verdict: OK TO DEPLOY` if there is nothing to report.

Then give the smallest fix for each finding. After a fix, re-run only the affected check.
