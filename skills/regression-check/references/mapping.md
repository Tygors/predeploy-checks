# Mapping changes to evidence

## Change classes

| Class | Examples | Default risk |
|---|---|---|
| `behavior` | branch, validation, default, rounding, error message, timeout, permission | REVIEW until a test asserts it |
| `interface` | function signature, route path or method, request or response field, CLI flag, env var, config key, event, schema | BLOCK if a consumer was not updated |
| `data` | migration, column rename, backfill, index, delete | BLOCK if destructive without rollback |
| `dependency` | package version, lockfile | REVIEW; do not audit CVEs here |
| `docs/style` | comments, formatting, tests-only, docs | SAFE unless it changes generated output |

When one hunk fits several classes, use the highest-risk class.

## Extract symbols from the diff

Read the new version of each changed line. Collect the names a test or consumer would use:

- Python: `def`, `class`, module-level constants, imported names, route decorators, keys in returned dicts, `os.environ[...]`, `os.getenv(...)`, CLI argument names.
- JavaScript/TypeScript: exported functions and components, route strings, `fetch`/`axios` paths, response field access, env vars (`process.env.X`), CLI flags.
- SQL: table names, column names, indexes, migration order.
- Config: keys in `.env`, YAML, TOML, JSON.

Ignore local variable renames and formatting unless they change a public name or output.

When using `git diff --no-index`, exit code 1 means the directories differ. Exclude generated files with a source pathspec (for example `-- '*.py'`) or read only the source files.

## Find tests that could cover it

Search test directories and test-like files for each symbol:

- function and class names
- route paths and HTTP methods
- response field keys
- env var names
- CLI flags
- test file names derived from the source file (`checkout.py` -> `test_checkout.py`, `checkout.test.ts`)

Then verify the test actually covers the change:

1. Does it call the changed function, route, or component?
2. Does it assert the changed value, branch, or field?
3. Would it fail if the change were reverted?

If the answer to any is no, it is a mention, not coverage. Examples:

- A test imports the module but asserts an unrelated function -> not coverage.
- A test asserts status 200 but the change is to the response body -> not coverage.
- A test calls `apply_discount(100, 101)` while the change affects `100` -> different boundary, not coverage.
- A test mocks the guard that the change modifies -> not coverage.
- A snapshot test that was regenerated with the change -> review it; it may only record the new output.

## Breaking-interface checklist

Search outside the diff for each interface change.

### Renamed or removed function, class, or flag

- Search callers and imports.
- Search tests.
- Search docs and examples.
- If a caller still uses the old name, `BLOCK`.

### Renamed or removed response field

- Search field access in clients: `obj.field`, `obj["field"]`, destructuring, generated types.
- Search tests and fixtures.
- If a client still reads the old field, `BLOCK`.

### Route path or method change

- Search frontend calls (`fetch`, `axios`, SDKs), server tests, and docs.
- If a caller still uses the old path or method, `BLOCK`.

### New or changed environment variable

- Search code usage and `.env.example`, `.env.sample`, README, Dockerfile, CI, and deploy config.
- A new required variable with no documented or configured value is `BLOCK`.
- A new optional variable with a safe default is `REVIEW`.

### Changed default

- Find callers that rely on the default.
- If no test covers the new default, `REVIEW`.

### Migration

- Is there a rollback or a forward fix?
- Is the table locked, data dropped, or a column renamed?
- A destructive migration with no rollback is `BLOCK`.

## Verdict rules

Choose the first matching verdict:

1. `NO CHANGES`: the diff is empty.
2. `BLOCK`: any of these is true:
   - an affected test fails;
   - a breaking interface still has an unupdated consumer;
   - a new required env var or config key is missing from deployment config;
   - a destructive migration has no rollback.
3. `REVIEW`: any of these is true:
   - a behavior change has no test that asserts the changed behavior;
   - an interface change exists but the consumer is unclear;
   - a dependency or lockfile changed;
   - only a snapshot records the change.
4. `SAFE`: every behavior change is covered by a test that would fail if reverted, and no interface is breaking.

A single `BLOCK` item makes the whole verdict `BLOCK`. Do not average risk.

## Examples

### BLOCK: renamed response field

Before:

```python
return {"total": order["total"]}
```

After:

```python
return {"amount": order["total"]}
```

`client.py` still reads `receipt["total"]`. The suite passes because no test calls `receipt()`. The consumer is broken even though the tests are green.

### REVIEW: changed boundary

Before:

```python
if percent > 100:
    raise ValueError(...)
```

After:

```python
if percent >= 100:
    raise ValueError(...)
```

The only test calls `101`. The change affects `100`, which no test exercises. This is a behavior change without coverage, not proof of a bug.

### SAFE: covered behavior change

Before:

```python
def fee(amount):
    return 0.0
```

After:

```python
def fee(amount):
    return round(amount * 0.03, 2)
```

The test was updated to assert `fee(100) == 3.0`. The test would fail if the fee change were reverted. Record it as covered and move on.

## Explaining to a non-coder

Use one sentence per finding:

> If this ships, <user> will see <impact>, because <file:line> still expects the old behavior and no test checks it.

Prefer concrete impact: "the receipt shows a blank total", "the 100% discount now errors", "the app fails to start without `TAX_RATE`".

## What is not a finding

- A diff you did not review because it is generated, vendored, or a lockfile; note it separately.
- A style or comment change.
- Missing tests for code the diff did not change.
- A green test that covers a different boundary; mention it as evidence, not as coverage.
- A theoretical external consumer with no evidence in the repository; mark it as a limit instead of `BLOCK`.
