# Checks

## 1. Secrets in shipped assets

Search HTML, JS, JSON, and source maps with these patterns:

| Type | ERE pattern | Severity |
|---|---|---|
| Anthropic API key | `sk-ant-[A-Za-z0-9_-]{20,}` | red |
| OpenAI API key | `sk-(proj-)?[A-Za-z0-9_-]{20,}` | red |
| AWS access key ID | `AKIA[0-9A-Z]{16}` | red |
| GitHub token | `ghp_[A-Za-z0-9]{36}` | red |
| GitHub fine-grained token | `github_pat_[A-Za-z0-9_]{22,}` | red |
| Stripe secret key | `sk_live_[0-9A-Za-z]{24,}` | red |
| Slack token | `xox[baprs]-[0-9A-Za-z-]{10,}` | red |
| Private key | `-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----` | red |
| Google API key | `AIza[0-9A-Za-z_-]{35}` | yellow |

Check Anthropic before OpenAI: `sk-ant-` matches both patterns.

Do not report:

- Stripe publishable keys (`pk_live_`, `pk_test_`).
- Supabase JWTs with `"role":"anon"`.
- Values the provider documents as public.

Report the type, file, line, and a redacted value (first 4 + `...` + last 4). Never print the full value.

## 2. JWT role

For each JWT (`eyJ...`) in client assets:

1. Split on `.` and decode the second segment as base64url.
2. Read the `role` claim.

- `service_role` means red. It bypasses row-level security.
- `anon` is allowed.
- Unknown roles are yellow.

## 3. Source maps

For `sourceMappingURL=` pointing to a reachable `.map`:

- Contains `sourcesContent`: red. The original source can be recovered.
- No `sourcesContent`: yellow. Structure and identifiers leak.

Also red:

- `sourceMappingURL=data:` inline maps.
- `*.map` files inside the build output with the same rules.

## 4. Public sensitive files

Probe only the target host:

`/.env`, `/.env.local`, `/.env.production`, `/.git/config`, `/.git/HEAD`, `/.DS_Store`.

Report only when both are true:

- Status is 200.
- The body matches the file type (`KEY=`, `[core]`, `ref:`, or a binary `.DS_Store` signature).

Ignore 200 responses that are the SPA HTML shell (`<html`, `<div id="root"`).

## 5. Verdict

- Any red finding: `Verdict: DO NOT DEPLOY`.
- Only yellow findings: `Verdict: DEPLOY WITH FIXES`.
- Nothing: `Verdict: OK TO DEPLOY`.
