# Report template

Keep the report short enough to read once. Put exactly one verdict line directly under the header.

Count changed source files after excluding generated, vendored, and lockfiles. Count changed behaviors, not hunks.

```text
REGRESSION CHECK - <scope> (<n> changed source files, <m> changed behaviors)
Verdict: <NO CHANGES | BLOCK | REVIEW | SAFE>

Changed behavior
| Change | Before -> After | User impact | Test evidence | Risk |
|---|---|---|---|---|
| <symbol> | <before> -> <after> (<file>:<line>) | <one sentence> | <test and line, or none> | <SAFE / REVIEW / BLOCK> |

Unverified or breaking
| Item | Why it matters | Evidence |
|---|---|---|
| <item> | <user impact> | <file>:<line> |

Affected tests
- `<command>` -> <passed / failed / not run> (<reason>)

Fix first
1. <smallest consumer update or test to add>
2. ...

Limits
- <what was not searched, sampled, or cannot be known>
```

## Filled example

Review of [`examples/regression-demo`](../../../examples/regression-demo/README.md), comparing `before/` with `after/`. Both suites pass.

This example matches the fixture so you can compare your own run. For another project, derive the rows from that project's diff.

```text
REGRESSION CHECK - examples/regression-demo (before -> after, 2 changed source files, 3 changed behaviors)
Verdict: BLOCK

Changed behavior
| Change | Before -> After | User impact | Test evidence | Risk |
|---|---|---|---|---|
| receipt field | total -> amount (after/app.py:16) | client.py:2 still reads total; the receipt total breaks | none | BLOCK |
| discount at 100 | 100 allowed -> 100 rejected (after/app.py:2) | a 100% discount now raises | only 101 is tested (after/test_app.py:9) | REVIEW |
| fee | 0.0 -> 3% (after/app.py:20) | receipts add a fee | test_fee expects 3.0 (after/test_app.py:22) | SAFE |

Unverified or breaking
| Item | Why it matters | Evidence |
|---|---|---|
| receipt consumer | the user sees a broken total | after/client.py:2 reads receipt["total"] |
| 100% discount | the changed boundary is not tested | after/test_app.py:9 calls 101 only |

Affected tests
- `python -m unittest discover -s examples/regression-demo/after` -> 4 passed (new version)
- `python -m unittest discover -s examples/regression-demo/before` -> 4 passed (baseline)

Fix first
1. Update client.py to read amount, or keep total until consumers migrate.
2. Add a test for apply_discount(100, 100) expecting ValueError.
3. Add a test that calls receipt() and asserts the field name.

Limits
- client.py is the only in-repo consumer found; external consumers were not checked.
- A green suite does not exercise receipt() or the 100% boundary.
```

## Report rules

- Start with the verdict. Do not bury it after the diff.
- List only changes that create risk or need evidence. Do not summarize every hunk.
- Cite the line in the new version, not only the old one.
- A test that exists but covers a different boundary is evidence of a gap, not coverage.
- Quote the consumer that still expects the old interface. "client.py:2 reads total" beats "possible breaking change".
- Put user impact in plain language: "the receipt shows a blank total", "the app fails to start without TAX_RATE".
- If tests could not run, say so in Limits and lower confidence. Do not present a static mapping as a run.
- If the diff is large, state what was sampled.
- Never print secrets, tokens, personal data, or production data found in the diff.
