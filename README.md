# predeploy-checks

**Checks for code you did not fully write.**

Agent skills for Claude Code, Cursor, and Codex. They inspect what an AI-built app actually ships and whether its tests actually prove anything, then explain the result in plain language before users find out.

**No telemetry. No uploads. Local-only.**

## The problem

Vibe coding makes the first version cheap. The expensive part comes later:

- A key ends up in the client bundle or a public preview.
- A source map lets anyone rebuild the source.
- The test suite is green because every test mocks the thing it is supposed to check.
- A change breaks a flow that no test covers, and nothing tells you.

If you build with AI and cannot review every line, "it works" is not evidence. These checks read the evidence for you.

Made for indie hackers, designers, product people, and developers working outside their main stack.

## The matrix

| Check | Question | When | Status |
|---|---|---|---|
| [secret-leak-check](skills/secret-leak-check/SKILL.md) | What does the shipped output expose? | Before deploy | Available |
| [test-audit](skills/test-audit/SKILL.md) | Do the tests actually prove anything? | Before merge | Available |
| regression-check | What did this change break? | Before merge | Planned |
| contract-check | Do the frontend, backend, and environment still agree? | Before deploy | Planned |
| deploy-smoke-check | Does the live preview actually work? | After deploy | Later |

## Install

One `SKILL.md` per check works in all three tools. From a clone of this repository:

```bash
git clone https://github.com/Tygors/predeploy-checks.git
cd predeploy-checks
```

Copy every check:

```bash
mkdir -p ~/.claude/skills && cp -r skills/* ~/.claude/skills/
```

Or install one:

```bash
mkdir -p ~/.claude/skills && cp -r skills/test-audit ~/.claude/skills/
```

| Tool | Skills directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |
| Codex | `~/.codex/skills/` |

Cursor also reads `~/.claude/skills/` and `~/.codex/skills/`, so a single Claude Code install is usually enough.

On Windows, run the commands in Git Bash, or copy the folder with PowerShell:

```powershell
Copy-Item -Recurse .\skills\* "$HOME\.claude\skills\"
```

## Use

Ask your agent:

> Check this preview URL before I deploy: https://example-preview.vercel.app

> Scan ./dist for leaked secrets and source maps before I ship.

> Audit my tests. They all pass, but I don't trust them.

## The checks

### secret-leak-check

Scans the deployable output, not the git history: built assets, preview URLs, source maps, and publicly readable `.env`, `.git`, and `.DS_Store` files.

Secrets are reported by type and location, never printed in full. Public-by-design keys such as Supabase `anon` and Stripe publishable keys are allowlisted.

| | secret-leak-check | gitleaks / detect-secrets |
|---|---|---|
| Scans | built assets and preview URLs | git history and repository files |
| Source maps | yes, including `sourcesContent` | no |
| Runs as | Claude Code / Cursor / Codex skill | standalone binary |
| Best for | pre-deploy gate | commit-time scanning |

### test-audit

Runs the existing test suite, then explains what each test actually proves. It flags tests that pass without proving the behavior they name: no assertion, assertion on a mock, tautological checks, skipped tests, and implementation-coupled tests.

It also maps critical behaviors such as login, payment, and data writes to the tests that cover them, and lists the behaviors with no real test.

Verdicts: `TRUSTWORTHY`, `PARTIAL`, `THEATER` (green, but not proving the critical path), or `NO TESTS`. It does not rewrite tests, and it does not treat line coverage as proof.

## Demo

Secret scan on a local build:

![Local build scan](https://github.com/Tygors/predeploy-checks/releases/download/v0.1.0/secret-leak-check-local.gif)

*Recorded from a real Claude Code session; output condensed.*

For the preview URL scan and the safe fixture, see [examples/vulnerable](examples/vulnerable/README.md).

Test audit on a suite that passes but proves little:

```bash
python -m unittest discover -s examples/weak-tests -v
```

Then ask your agent to audit the tests. The fixture and the expected findings are in [examples/weak-tests](examples/weak-tests/README.md).

## Design rules

- One question per check.
- Evidence over scores: every finding cites `file:line`.
- Plain language: define assertion, mock, snapshot, and coverage on first use.
- Read-only unless the user asks for a fix.
- Local-only: no telemetry, no uploads.
- No configuration; detect the stack.
- High signal: a false alarm costs more trust than a missed edge case.

## Roadmap

- `regression-check`: map a diff to affected tests and flag changed behavior with no test.
- `contract-check`: find drift between frontend calls, backend routes, and environment variables.
- `deploy-smoke-check`: verify pages, console errors, and key flows on a live preview.
- An optional CLI to run the matrix in one command.

## Contributing

Reports of false positives, missed findings, and weak tests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the issue templates.

## License

MIT
