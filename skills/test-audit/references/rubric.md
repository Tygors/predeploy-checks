# Audit rubric

## Classes

| Class | Definition | What it does not do |
|---|---|---|
| `PROVES` | Asserts a specific observable outcome that would change if the behavior broke. The assertion is on the result, not on a fake. | It does not prove the whole feature, only the stated case. |
| `WEAK` | Asserts something real but insufficient: only the happy path, only a type or status, a mocked guard, an implementation detail, or a snapshot. | It does not catch the failure it appears to cover. |
| `THEATER` | Passes without checking the result: no assertion, assertion on a mock, input asserted against itself, or a body that only constructs objects. | It does not test the unit at all. |
| `SKIPPED` | Skipped, focused away, marked todo, or expected to fail. | It does not run in the normal suite. |

## Decision order

1. Is it skipped, focused away, or todo? -> `SKIPPED`.
2. Is there at least one assertion outside of a mock? If no -> `THEATER`.
3. Is the only assertion on a mock, or does it compare a value to itself? -> `THEATER`.
4. Would the test still pass if the implementation returned `None`, `0`, `{}`, or an empty response? -> `WEAK` at best. If it does not assert the result at all, `THEATER`.
5. Does the assertion check a specific result, error, or state transition of the behavior under test? If no -> `WEAK`.
6. Does the test mock the guard, branch, or unit that the behavior depends on? -> `WEAK` at best.
7. Does deleting the implementation line or error branch make the test fail? If no -> not covered.
8. Otherwise -> `PROVES`.

## Examples

### PROVES

```python
self.assertEqual(apply_discount(100, 10), 90.0)
with self.assertRaises(ValueError):
    apply_discount(100, 101)
```

```js
expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
await expect(createUser({ name: '' })).rejects.toThrow('name is required');
```

The expected value is explicit. Removing the calculation or the validation makes the test fail.

### WEAK

```python
self.assertIsNotNone(apply_discount(100, 10))  # would pass for any number
```

```python
@patch("app._check_balance", return_value=True)
def test_transfer(self, _check_balance):
    self.assertEqual(transfer(100, 10), 90)
```

The first checks existence, not the discount. The second mocks the overdraft guard, so it cannot catch a broken guard.

```js
expect(response.status).toBe(200);  // says nothing about the body or the write
```

### THEATER

```python
def test_does_not_crash(self):
    apply_discount(100, 10)  # no assertion
```

```python
def test_calls_api(self):
    client.post = Mock()
    create_user({"name": "A"}, client)
    client.post.assert_called_once()  # proves a call, not a user
```

```js
test('adds', () => {
  const result = add(1, 2);
  expect(result).toBe(result);  // tautology
});
```

```js
test('renders', () => {
  render(<Button />);
  // snapshot without review, or no assertion at all
});
```

### SKIPPED

```python
@unittest.skip("later")
def test_rejects_over_100_percent(self):
    ...
```

```js
test.only('happy path', () => { ... });  // every other test is silently skipped
```

## Smells to flag

- No assertion, or an assertion inside a `try`/`catch` that swallows the failure.
- Asserting on a mock call instead of the result.
- Mocking the function or module under test.
- Asserting a value against itself, or `expect(true).toBe(true)`.
- Only asserting truthiness for a value that is always truthy.
- Only asserting a status code, a type, or "does not throw".
- Snapshot tests with no review and no small, stable output.
- Implementation coupling: private methods, exact call counts, internal ordering.
- Time, randomness, network, or database without control; `sleep` used to wait.
- Test order dependence or shared mutable state.
- Tests that import production configuration, credentials, or live endpoints.
- A test suite that passes while every test is focused away or undiscovered.

## Critical behavior checklist

Use this to build the behavior list. Skip categories that do not exist in the project.

- authentication, sessions, and logout
- authorization and role checks
- payment, credits, refunds, and billing
- create, update, delete, and restore of user data
- input validation and rejected inputs
- error states and empty states
- external API failure and timeout handling
- file upload, import, and export
- destructive CLI or admin operations
- required environment variables and startup checks
- rate limits and permission boundaries

## Sampling large suites

- Audit critical suites fully.
- For large non-critical suites, sample by risk: files changed recently, files with the most conditionals, and files named after user-facing behavior.
- State the sample and the reason. Do not present a sample as a full audit.
- Report the count of tests classified, not just the count of tests found.

## Explaining to a non-coder

For each finding, use this shape:

> This test says it checks X, but it only checks Y. If X broke, this test would still pass. X matters because <user impact>.

Define terms on first use:

- **Assertion:** the line that fails when the result is wrong.
- **Mock:** a fake replacement for a real dependency. Useful for isolating code, dangerous when it replaces the thing being tested.
- **Snapshot:** a saved copy of output compared later. It catches changes, not correctness.
- **Coverage:** the percentage of lines that ran. A line can run without any assertion.

## What is not a finding

- Low line coverage by itself.
- Slow tests, unless they hide flakiness or block the suite.
- Style, naming, or folder structure.
- Missing tests for trivial getters with no behavior.
- A green test that is genuinely narrow but correct. Mark it `PROVES` and state its scope.

## Verdict guidance

Choose the first verdict that matches:

1. `NO TESTS`: no runnable tests were found.
2. `THEATER`: the suite looks green, but no critical behavior has a `PROVES` test (test theater).
3. `PARTIAL`: at least one critical behavior has a `PROVES` test, but material gaps remain.
4. `TRUSTWORTHY`: every critical behavior has a `PROVES` test, and no critical path is theater.

If both `THEATER` and `PARTIAL` seem true, `THEATER` wins. One real test does not rescue a suite that leaves every other critical behavior unproven.
