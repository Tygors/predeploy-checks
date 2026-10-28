# Report template

Use this shape. Keep it short enough to read once. Put exactly one verdict line directly under the header.

Count skipped tests in `<n> tests`, and report them separately.

```text
TEST AUDIT - <project or suite> (<framework>, <n> tests, <skipped> skipped)
Verdict: <TRUSTWORTHY | PARTIAL | THEATER | NO TESTS>

What the suite proves
- <behavior> (<file>:<line>)
- ...

What it does not prove
- <behavior> (<file>:<line>)
- ...

Tests that prove less than they claim
| Test | Location | What it actually checks | Class |
|---|---|---|---|
| <name> | <test definition file>:<line> | <one sentence; cite the assertion line if different> | <WEAK / THEATER / SKIPPED> |

Critical behaviors without a real test
| Behavior | Why it matters | Current evidence |
|---|---|---|
| <behavior> | <user impact> | <mock / type check / skipped / none> |

Fix first
1. <smallest test to add or change>
2. ...

Limits
- <what was not run, sampled, or cannot be known>
```

## Filled example

Audit of [`examples/weak-tests`](../../../examples/weak-tests/README.md). The suite passes, but most tests do not prove the behavior they name.

This example deliberately matches the fixture so you can compare your own run. For another project, derive the rows from that project's tests.

```text
TEST AUDIT - examples/weak-tests (unittest, 5 tests, 1 skipped)
Verdict: PARTIAL

What the suite proves
- A negative transfer amount is rejected (test_app.py:26).
- A transfer returns balance - amount when the balance check is forced to pass (test_app.py:24).

What it does not prove
- That apply_discount returns the correct amount. test_app.py:10 checks the type only.
- That an overdraft is rejected. test_app.py:22 replaces _check_balance with a fake that always passes.
- That discount boundaries 0, 100, and 101 are handled. The only boundary test is skipped (test_app.py:15).

Tests that prove less than they claim
| Test | Location | What it actually checks | Class |
|---|---|---|---|
| test_returns_a_number | test_app.py:8 | The result is an int or float (assertion at test_app.py:10); any number passes | WEAK |
| test_does_not_crash_on_valid_input | test_app.py:12 | No assertion; the call at test_app.py:13 is the whole test | THEATER |
| test_rejects_over_100_percent | test_app.py:15 | Skipped ("boundaries later") | SKIPPED |
| test_successful_transfer | test_app.py:23 | Mocks the balance guard (test_app.py:22); only the subtraction is checked (test_app.py:24) | WEAK |

Critical behaviors without a real test
| Behavior | Why it matters | Current evidence |
|---|---|---|
| Discount math | A wrong price is charged | Type check only |
| Overdraft rejection | Balance can go negative or funds are lost | Guard is mocked in the only success test |
| Discount boundaries | 0/100/101 can charge the wrong amount | Skipped only |

Fix first
1. Replace the type check with an exact value: apply_discount(100, 10) == 90.0.
2. Add a transfer test that does not mock _check_balance and expects ValueError for amount > balance.
3. Unskip the boundary test and add cases for 0 and 100.
4. Delete the no-assertion test or make it assert a specific result.

Limits
- The suite was small and audited completely.
- This audit checks the evidence in the tests, not the correctness of the fee or balance rules.
```

## Report rules

- One row per test that does not prove behavior. Do not list every healthy test.
- Quote or point to the assertion. Never ask the reader to trust a label.
- Put the user impact in the "Why it matters" column. "A wrong price is charged" beats "lack of assertion".
- Order fixes by risk, then by size. One behavior-level test is better than a suite rewrite.
- If tests could not run, say so in Limits and lower confidence. Do not present a static audit as a run.
- If the suite is large, state the sample in Limits.
- Never print secrets, tokens, personal data, or production data found in fixtures.
