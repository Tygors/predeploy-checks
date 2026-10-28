---
name: test-audit
description: Explain what a project's tests actually prove and what they miss. Use before shipping AI-written code, when tests pass but the user does not trust them, or when the user asks what their tests cover. Flags tests with no meaningful assertions, mock-only tests, skipped tests, and critical behaviors with no real coverage.
---

# Test Audit

Most test suites pass. Passing is not proof.

This skill answers one question: **what do these tests actually prove, and what do they not?** It is written for people who did not write the tests and may not read code fluently. Explain findings in plain language.

## When to use

- The user is about to ship AI-written code.
- The user asks whether their tests are real, trustworthy, or meaningful.
- All tests pass, but the user does not trust the result.
- A bug reached production that the tests should have caught.
- The user wants to know which behavior is safe to change.

## Rules

- Read-only by default. Do not edit tests or production code unless the user asks.
- Cite evidence for every judgment: `file:line` plus the assertion, missing assertion, or mock.
- Explain jargon on first use: assertion, mock, snapshot, coverage.
- Run only the project's existing test command. Do not install packages.
- Ask before running tests that need network, a database, credentials, or production services.
- Only run tests in a local checkout the user trusts. Tests execute repository code.
- Never upload code, test output, or findings.
- Do not call a test worthless without showing why it would still pass if the behavior broke.
- A clean audit is not proof that the app has no bugs. Say so in the report.
- Match the user's language in the report.

## Step 1: Find the test command and scope

Inspect the repository for the documented way to run tests:

- `package.json` scripts, `vitest`, `jest`, `mocha`, `playwright`, `cypress`
- `pytest.ini`, `pyproject.toml`, `tox.ini`, `unittest`, `Makefile`
- CI workflows that run the suite

Prefer the documented command over a guess. Do not install missing dependencies.

Record the framework, the number of test files, and the number of test cases. If there are several suites, audit the one covering critical user behavior first and say which suites were not audited.

If there are no runnable tests, use `Verdict: NO TESTS`, list the critical behaviors, and propose the smallest first test. Do not invent a pass.

## Step 2: Run the suite

Run with a timeout. Capture:

- passed, failed, skipped, todo, and focused (`.only`) tests
- environment failures separately from logic failures
- warnings that suggest flakiness or hidden failures

If dependencies are missing or the suite cannot start, do a static audit and say that no runtime evidence was available.

Treat these as red flags:

- `.only` / `fit` / `fdescribe` in committed tests: the rest of the suite silently does not run.
- `.skip` / `xit` / `@pytest.mark.skip` / `xfail` without a linked reason.
- Test files that exist but are not discovered by the configured runner.
- A test command that exits successfully without running any tests.

## Step 3: Audit each test

For every test in a critical suite, or a risk-based sample in a large suite, fill in:

| Field | Meaning |
|---|---|
| Test | Name and the test definition's `file:line` |
| Claim | One plain sentence: "This test claims that ___." |
| Evidence | The assertion, quoted, with the assertion's `file:line` |
| Mocks | What is replaced by a fake |
| Failure path | Does it exercise a rejected input or error branch? |
| Class | `PROVES`, `WEAK`, `THEATER`, or `SKIPPED` |

When the definition and assertion are on different lines, cite both.

Use the classification rules in `references/rubric.md`.

Two quick tests decide most cases:

1. **The constant test.** If the implementation returned `None` or an empty response, would this test still pass? If yes, it is proving at most a weak property. If it never asserts the result, it is theater.
2. **The deletion test.** Delete the validation or error branch the test is supposed to cover. Does the test fail? If not, that behavior is untested.

## Step 4: Map critical behaviors to tests

Build a behavior list from entry points, not from the test files: routes, API handlers, CLI commands, exported functions, user flows, and startup configuration.

Prioritize behaviors where failure is expensive:

- authentication and permissions
- payment, credits, and billing
- creating, updating, and deleting user data
- input validation and error states
- external API failure handling
- destructive operations
- required environment variables and startup checks

For each behavior, record `covered`, `weak`, or `untested`. A test that mocks the behavior's guard counts as weak or untested, not covered.

Do not demand 100% coverage. Demand that the failures a user would feel are tested.

## Step 5: Report

Use the template in `references/report.md`. Put exactly one verdict line directly under the header, chosen in this order:

1. `Verdict: NO TESTS` - no runnable tests were found.
2. `Verdict: THEATER` - the suite looks green, but no critical behavior has a `PROVES` test (test theater).
3. `Verdict: PARTIAL` - at least one critical behavior has a `PROVES` test, but material gaps remain.
4. `Verdict: TRUSTWORTHY` - every critical behavior has a `PROVES` test, and no critical path is theater.

Apply the first verdict that matches. Do not skip a higher rule because a lower one also seems true.

Then list the smallest fixes first. Prefer adding one behavior-level test over rewriting the suite.

Do not write tests unless the user asks. When asked, add one test per behavior, assert an exact observable outcome, and do not mock the unit under test.

## Step 6: Re-run after fixes

After a fix, re-run only the affected tests and re-classify them. Update the verdict only if the critical gap is closed.

## Limits

- This is an audit of evidence, not a proof of correctness.
- Static classification can be wrong; quote the assertion so the user can check.
- Large suites are sampled. Say what was sampled.
- Passing tests do not cover untested behavior, and line coverage does not prove behavior.
