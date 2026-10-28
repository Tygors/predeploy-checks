---
name: regression-check
description: Review a change set before merging to find behavior that changed without a test. Use when the user asks what a diff or recent commit might break, before merging AI-written code, or before shipping a change. Maps changed code to affected tests, flags untested behavior changes and breaking interfaces, and reports SAFE / REVIEW / BLOCK.
---

# Regression Check

A green suite is not the same as a tested change.

Most tests protect behavior that existed before the diff. A change can add a branch, rename a response field, or alter a default while every old test still passes. This skill reviews the change itself and answers one question: **what did this change break, and what evidence do we have that it did not?**

It is written for people who did not write the change and may not read code fluently. Explain impact in plain language.

## When to use

- Before merging, committing, or shipping a change.
- The user asks "what did this break?" or "is this safe to merge?"
- AI produced a multi-file change and the user cannot review every hunk.
- A bug fix needs a regression test.
- Before a preview deploy.

## Rules

- Read-only by default. Do not edit code or tests unless the user asks.
- Establish the exact change set first. Do not review unrelated code.
- Cite the changed line (`file:line` in the new version) and the test or consumer.
- Explain user impact in one sentence per finding.
- Run only existing tests. Do not install packages.
- Ask before tests that need network, a database, credentials, or production services.
- Only run tests in a local checkout the user trusts. Tests execute repository code.
- A passing test does not prove a change is safe. Say which behavior is unverified.
- Never upload code, diffs, or findings.
- Match the user's language in the report.

## Step 1: Establish the change set

Use the input the user names:

- working tree: `git status --short`, `git diff`, `git diff --cached`
- branch: `git diff <base>...HEAD`, plus `git log --oneline <base>..HEAD`
- commit: `git show <sha>`
- patch file: read it
- two directories: `git diff --no-index -- <before> <after>`

`git diff --no-index` exits 1 when the directories differ. That is not an error. If generated files appear in the diff, add a source pathspec (for example `-- '*.py'`) or review only the source files, and say what was excluded.

Record changed source files, changed lines, and whether the change is staged. Count the new-side files in a two-directory comparison. If there is no diff, report `Verdict: NO CHANGES` and stop.

Ignore generated files, vendored code, and lockfiles for behavior analysis, but note lockfile changes as dependency changes. If the diff is large, audit non-generated files first and say what was sampled.

## Step 2: Describe each behavior change

For every non-trivial hunk, write one sentence:

> Before: ___. After: ___. A user or caller would see ___.

Classify each change with `references/mapping.md`:

- `behavior`: control flow, return value, default, validation, error, rounding, timeout, permission.
- `interface`: function signature, route, request or response field, CLI flag, env var, config key, event or schema.
- `data`: migration, column rename, backfill, index.
- `dependency`: package version or lockfile.
- `docs/style`: comments, formatting, tests-only.

Skip comments and formatting unless they change generated output.

## Step 3: Map changes to tests

For each changed behavior and interface, extract the symbols: function names, classes, routes, field keys, env vars, flags.

Find tests that mention them:

- test directories and naming conventions
- imports and call sites in test files
- route paths and field names in assertions
- fixtures and factories

A mention is not coverage. The test must call the changed code and assert the changed behavior. State when a test only imports the module, asserts an unrelated value, or covers a different boundary.

Run the new version's tests first if the project has a documented command. Run the old version only to establish a baseline when the command or expected result is unclear. If no command is documented, do a static mapping only, say that tests were not run, and do not invent a command. Record pass, fail, and environment failures separately.

## Step 4: Find breaking interfaces

Define the target as the repository root that contains the new version. In a two-directory comparison, search the new-side directory first, then the parent repository for consumers that were not copied into the fixture.

For every interface change, search the target for consumers outside the diff:

- callers of a renamed or removed function or flag
- clients that read a renamed response field
- route paths used by frontend code
- env vars used in code but missing from `.env.example`, docs, CI, or deploy config
- migrations without a rollback or backfill
- changed defaults that callers rely on

If a consumer was not updated, the change is breaking. State the file and line.

## Step 5: Decide the verdict

Choose the first verdict that matches:

1. `Verdict: NO CHANGES` - there is no diff.
2. `Verdict: BLOCK` - an affected test fails; a breaking interface has an unupdated consumer; a required env var or config key is missing; or a destructive migration has no rollback.
3. `Verdict: REVIEW` - a behavior change has no test that asserts it, an interface change has an unclear consumer, or a dependency change needs review.
4. `Verdict: SAFE` - every behavior change is covered by a test that would fail if reverted, and there is no breaking interface.

## Step 6: Report

Use `references/report.md`. Put the verdict directly under the header. List only changes that create risk or need evidence; do not dump the whole diff.

Then list the smallest fixes first:

1. Update the consumer or keep the old interface.
2. Add one regression test for the changed behavior.
3. Update config or docs for a new env var.

Do not write tests unless the user asks. When asked, add one test per changed behavior, assert an exact observable outcome, and include the boundary that changed.

## Step 7: Re-check after fixes

Re-run only the affected tests and re-evaluate the changed items. Change the verdict only when the blocking evidence is resolved.

## Limits

- Static mapping misses dynamic calls, reflection, and external consumers.
- Passing tests do not prove behavior that no test exercises.
- This is a diff-scoped check, not a full audit. Use `test-audit` for suite quality and `contract-check` for cross-service contracts.
- Do not run production traffic or destructive migrations to verify a change.
