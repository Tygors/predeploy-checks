# Regression demo fixture

A small change set with one safe change, one untested boundary change, and one breaking field rename. Both versions pass their tests, which is the point: a green suite can still hide a broken consumer.

The code and data are fake. Nothing here talks to a network or a database.

## Review the change

From the repository root:

```bash
git diff --no-index -- examples/regression-demo/before examples/regression-demo/after -- '*.py'
```

The `*.py` pathspec keeps generated `__pycache__` files out of the diff.

Then ask your agent:

> Review the change from examples/regression-demo/before to examples/regression-demo/after before I merge.

## Run both versions

```bash
python -B -m unittest discover -s examples/regression-demo/before
python -B -m unittest discover -s examples/regression-demo/after
```

Both suites pass.

## Expected findings

- `BLOCK`: `receipt()` returns `amount` instead of `total`; `client.py:2` still reads `total`.
- `REVIEW`: `apply_discount(100, 100)` now raises; the only boundary test uses `101`.
- `SAFE`: `fee()` changes from `0.0` to `3%`; `test_fee` asserts `3.0`.

Expected verdict: `BLOCK`.

The fixture deliberately leaves `after/client.py` unchanged. In a real change, the consumer update would be part of the diff, and the regression check would see it.
