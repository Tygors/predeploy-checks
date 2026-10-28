---
name: contract-check
description: Check whether a project's frontend calls, backend routes, and environment variables still agree. Use before deploying, after AI-generated changes, or when the user asks whether client, server, and config are in sync. Reports IN SYNC / DRIFT / BROKEN / NO CONTRACT with file:line evidence.
---

# Contract Check

The frontend and backend can both compile while disagreeing about the API. A client calls a route the server no longer has; a response field is renamed on one side; a required env var exists in code but not in `.env.example`. Nothing fails until a user hits it.

This skill answers one question: **do the client, server, and environment still agree?** It reads the repository statically, compares the surfaces, and explains the mismatch in plain language.

Written for people who did not write the integration and may not read code fluently.

## When to use

- Before deploying, especially after AI-generated changes across client and server.
- The user asks whether the frontend and backend are in sync.
- The user asks whether all environment variables are configured.
- A route or response field was renamed.
- A preview deploy fails with 404, 422, or 500 on a specific call.

For a specific diff, use `regression-check` first; this skill checks the whole current contract, not just the change.

## Rules

- Read-only by default. Do not edit code or config unless the user asks.
- Cite both sides when both exist: client `file:line` and server `file:line`. For a missing route or an undeclared variable, cite the side that exists and say the other side is absent.
- Only report a missing route as `BROKEN` when the method and path are statically resolvable. If the URL is built dynamically, report `DRIFT` and say what could not be resolved.
- Do not treat public client prefixes (`VITE_`, `NEXT_PUBLIC_`, `REACT_APP_`, `PUBLIC_`) as secret leaks. `secret-leak-check` covers shipped secrets.
- Do not claim field-level type safety unless an OpenAPI/GraphQL schema or a contract test proves it.
- Run only documented contract tests. Do not install packages.
- Ask before running contract tests that need network, a database, credentials, or a running server.
- Never upload code, route lists, or findings.
- Match the user's language in the report.

## Step 1: Define the scope

Find the parts of the repository that participate in the contract:

- frontend source and API client code
- backend routes, controllers, or server handlers
- `.env.example`, `.env.sample`, `.env.template`, Dockerfile, compose, CI, and deploy config
- OpenAPI/Swagger or GraphQL schema, if present
- contract tests (Pact, schemathesis, Dredd, OpenAPI validators)

If the repository has no client calls, server routes, or env usage, report `Verdict: NO CONTRACT` and stop.

In a monorepo, name the frontend and backend roots you compared. Do not mix unrelated apps.

## Step 2: Inventory server routes

Extract method, normalized path, and `file:line` for each route. Use the patterns in `references/detection.md` for Flask, FastAPI, Express, Next.js, Django, and OpenAPI.

If an OpenAPI spec exists, record its paths and methods separately. The spec is another claim about the contract, not automatic proof.

## Step 3: Inventory client calls

Extract method, normalized path, and `file:line` for each call: `fetch`, `axios`, `ky`, `useSWR`, and similar.

- Default `fetch` to `GET` only when no `method` option is present.
- Strip query strings and origins.
- Normalize path parameters: `:id`, `{id}`, `<int:id>`, `[id]`, and `${id}` all become `:param`.
- Mark external origins, SDK calls, and fully dynamic paths as unresolved. A dynamic base with a comparable absolute path is handled in Step 4; do not discard it.
- Do not guess a concrete path from a variable name.

## Step 4: Compare routes

Match client calls to server routes by method and normalized path.

- A resolved call with no matching route in either the code or the spec is `BROKEN`.
- A call that matches the path but not the method is `BROKEN`; report the methods the server does define.
- If a template literal starts with a dynamic base but leaves an absolute path (`${API_BASE}/api/users`), compare the literal path and note the unresolved origin. A dynamic origin alone is not a finding; if the literal path matches, mark it matched and say the origin was unverified. `DRIFT` applies only when the path itself cannot be compared.
- An unresolved path is `DRIFT`; state what could not be resolved.
- A server route with no client call is not automatically a problem; it may be public or used by another app. Mention it as unused surface only if the user asks.
- If a client call matches the OpenAPI spec but not the code routes, report `DRIFT`: the spec and code disagree, and the call has no code route. `BROKEN` requires no match in either the code or the spec.
- If the OpenAPI spec disagrees with the code routes in another way, report `DRIFT` and name both sources.
- Do not compare response fields unless Steps 2 and 6 found a schema or contract test.

## Step 5: Check the environment contract

Extract used env vars and whether each is required:

- required: `os.environ["X"]`, `os.environ.get("X")` with no default, `process.env.X` or `import.meta.env.X` with no adjacent `||` or `??` fallback
- optional: `os.getenv("X", default)`, or a JS access with an adjacent fallback

Extract declared vars from `.env.example`, `.env.sample`, `.env.template`, Dockerfile, compose, CI, and deploy config.

- A required var used in code but declared in no machine-readable config is `BROKEN`.
- A var declared only in README or deployment docs, not in machine-readable config, is `DRIFT` with a note; it may not be set at deploy time.
- An optional var used with a safe default and declared nowhere is a note, not a failure.
- A declared var used nowhere is `DRIFT`; it may be stale or reserved.
- A public client prefix is expected in the client bundle; do not report it as a secret.

Ignore runtime-provided names such as `NODE_ENV`, `MODE`, `DEV`, `PROD`, `SSR`, `BASE_URL`, `PATH`, `HOME`, `PWD`, `SHELL`, `USER`, `TZ`, `LANG`, `CI`, and `PORT` when the platform provides it, unless the project clearly owns them.

## Step 6: Use contract tests when present

If the project has a documented contract test command (`test:contract`, `schemathesis`, `dredd`, a Pact suite, or an OpenAPI validator), it is stronger evidence than static matching.

- Run it only if it is safe locally and does not need production services.
- Ask before a command that starts servers, databases, or uses credentials.
- A failure is `BROKEN`.
- A pass proves only the surfaces the test covers; say so.

Do not install a contract testing tool just to complete the audit.

## Step 7: Decide the verdict

Choose the first verdict that matches:

1. `Verdict: NO CONTRACT` - no client calls, server routes, or env usage were found.
2. `Verdict: BROKEN` - a resolved client call has no matching route in either the code or the OpenAPI spec; a required env var is undeclared in machine-readable config; a contract test fails; or the client and server require different methods.
3. `Verdict: DRIFT` - a path is unresolved; a call matches only the spec, not the code; the spec and code disagree; a declared env var is unused; or a var is declared only in docs.
4. `Verdict: IN SYNC` - all resolved paths match, required env vars are declared in machine-readable config, and no schema or contract test contradicts the code.

## Step 8: Report

Use `references/report.md`. Put the verdict directly under the header.

Explain each finding as:

> `<client call>` expects `<method> <path>`, but `<server>` defines `<what exists>`. A user would see `<impact>`.

Then list the smallest fixes first: add or remove the route, update the client, or declare the env var.

## Step 9: Re-check after fixes

Re-run the affected comparison and contract test. Change the verdict only when the mismatch is resolved.

## Limits

- Static analysis misses dynamic URLs, SDK calls, GraphQL operations, and generated clients. Mark them unresolved instead of guessing.
- Response field compatibility is not checked unless a schema or contract test exists.
- Authentication, status codes, business logic, and runtime behavior are out of scope; `deploy-smoke-check` covers live behavior.
- External consumers outside the repository are not checked.
- A green contract test covers only the surfaces it exercises.
