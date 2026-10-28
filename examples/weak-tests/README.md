# Weak tests fixture

A deliberately misleading test suite. Every test passes, but most of them do not prove the behavior they appear to cover.

The code and data are fake. Nothing here talks to a network or a database.

## Run the suite

```bash
python -m unittest discover -s examples/weak-tests -v
```

Expected result:

```text
Ran 5 tests in ...
OK (skipped=1)
```

## What is wrong

| Test | Problem |
|---|---|
| `test_returns_a_number` | Checks the type of the discount, not the discount. It would pass for `0` or `999`. |
| `test_does_not_crash_on_valid_input` | Has no assertion. It passes as long as the call does not raise. |
| `test_rejects_over_100_percent` | Skipped, so the upper boundary is not tested. |
| `test_successful_transfer` | Mocks `_check_balance`, which is the overdraft guard. It proves the subtraction, not the balance check. |
| `test_rejects_negative_amount` | Real: it checks a rejected input. |

## Untested critical behavior

- The discount amount is never checked against an expected value.
- An overdraft is never rejected in a test that runs the real balance check.
- Discount boundaries (`0`, `100`, `101`) are only present in a skipped test.

## Expected verdict

`Verdict: PARTIAL` - one failure path is proven, but the money paths are not.

Ask your agent:

> Audit the tests in examples/weak-tests. They pass, but I don't trust them.
