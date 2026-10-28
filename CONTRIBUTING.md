# Contributing

Thanks for helping make shipped apps a little safer.

## Ways to contribute

- Report a false positive or a missed finding using the issue templates.
- Improve an existing check, its rubric, or its fixture.
- Propose a new check for the matrix.
- Improve the README, demos, or install instructions.

## Ground rules

- One question per check, one verdict.
- Evidence over scores. Every finding cites a file and line.
- Plain language. The reader may not read code fluently; define jargon on first use.
- Read-only by default. A check changes code only when the user asks.
- Local-only. No telemetry, uploads, or third-party services.
- High signal. A false alarm costs more trust than a missed edge case.
- Never include a real secret, token, personal data, or production data in an issue, pull request, fixture, or test. Use clearly fake values.
- If a real credential was exposed, rotate it first.

## Secret patterns

These rules apply to `secret-leak-check`.

- High-confidence patterns only. The check is pattern-based and deliberately does not use entropy scanning.
- Public-by-design keys stay out of findings: Supabase `anon`, Stripe publishable keys, and anything the provider documents as public.
- Add the type, ERE pattern, and severity to `skills/secret-leak-check/references/checks.md`.
- Add a fake fixture under `examples/vulnerable/` if the pattern needs a demo.
- Explain the false-positive impact of a new pattern in the pull request.

## Test audit

These rules apply to `test-audit`.

- A classification must quote or cite the assertion, missing assertion, or mock.
- Do not flag every mock. A mock is a problem when it replaces the behavior under test, not when it isolates an unrelated dependency.
- Prefer examples that would pass if the implementation returned a constant.
- Add deliberately misleading tests to `examples/weak-tests/`, not to a real project.
- Do not treat line coverage as proof of behavior.
- Keep the report understandable to someone who does not write tests for a living.

## Regression check

These rules apply to `regression-check`.

- Review only the change set the user names. Do not audit unrelated code.
- Cite the new-version line for every finding.
- A test that mentions a symbol is not coverage. It must call the changed code and assert the changed behavior.
- Search for consumers when an interface changes: callers, response fields, routes, env vars, migrations.
- Do not flag a missing test for code the diff did not touch.
- Add deliberately risky changes to `examples/regression-demo/`, not to a real project.

## Contract check

These rules apply to `contract-check`.

- Compare only statically resolvable methods and paths. Mark dynamic URLs as unresolved.
- Cite both sides when both exist. For a missing route or undeclared var, cite the existing side and say the other is absent.
- A path that exists with a different method is a method mismatch, not a missing path.
- Do not treat public client env prefixes as secrets.
- Do not claim response fields disagree without an OpenAPI schema or contract test.
- Add static drift examples to `examples/contract-demo/`, not to a real project.

## Preview check

These rules apply to `preview-check`.

- Scan only the origin the user names. Do not follow other origins.
- Use GET and HEAD only. Do not log in, submit forms, click through flows, or mutate data.
- Keep the limits: 10 pages total, 30 assets total, 15 seconds per request.
- Do not claim console or network checks unless a browser driver actually captured them.
- Localhost over HTTP is not a mixed-content situation.
- Add broken previews to `examples/preview-demo/`, not to a real deployment.

## Adding a check

1. Create `skills/<check-name>/SKILL.md` with frontmatter, when-to-use, rules, a workflow, and one verdict line.
2. Put long rubrics, patterns, and report templates in `skills/<check-name>/references/`.
3. Add a small, fake fixture under `examples/`.
4. Update `README.md`.
5. Keep one behavior or one check per pull request.

A check should be cheap to run and hard to fake. If it needs extensive configuration or produces noisy findings, it is not ready.

## Local testing

Secret scan:

```bash
python examples/vulnerable/make_demo.py
```

Then ask your agent:

> Check `./examples/vulnerable/dist` before I deploy.

Or serve the fixture and scan the URL:

```bash
python -m http.server 8000 --directory examples/vulnerable/dist
```

The expected findings are listed in `examples/vulnerable/README.md`.

Test audit:

```bash
python -m unittest discover -s examples/weak-tests -v
```

Then ask your agent:

> Audit the tests in examples/weak-tests. They pass, but I don't trust them.

The expected audit is described in `examples/weak-tests/README.md`.

Regression check:

```bash
git diff --no-index -- examples/regression-demo/before examples/regression-demo/after -- '*.py'
python -B -m unittest discover -s examples/regression-demo/after
```

Then ask your agent:

> Review the change from examples/regression-demo/before to examples/regression-demo/after before I merge.

Both suites pass; the expected findings are described in `examples/regression-demo/README.md`.

Contract check:

```text
> Check whether the frontend, backend, and environment agree in examples/contract-demo.
```

The fixture is static; no server or dependency is needed. The expected findings are in `examples/contract-demo/README.md`.

Preview check:

```bash
python examples/preview-demo/server.py 8000
```

In another terminal, ask your agent:

> Check http://localhost:8000 before I promote it.

The fixture and expected findings are in `examples/preview-demo/README.md`. Stop the server with `Ctrl+C`.

## Pull requests

- Explain what failure the change catches and what false positives it may add.
- Update the README or references when behavior changes.
- Keep fixtures fake.
- Do not add dependencies without a clear reason.
