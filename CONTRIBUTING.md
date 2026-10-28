# Contributing

Thanks for helping make shipped apps a little safer.

## Ways to contribute

- Report a false positive or a missed secret using the issue templates.
- Add a high-confidence secret pattern.
- Improve the README, demo fixture, or checks.

## Ground rules

- High-confidence patterns only. This skill is pattern-based and deliberately does not use entropy scanning.
- Never include a real secret in an issue, pull request, fixture, or test. Use clearly fake values.
- Public-by-design keys stay out of findings: Supabase `anon`, Stripe publishable keys, and anything the provider documents as public.
- If a real credential was exposed, rotate it first.

## Adding a pattern

1. Add the type, ERE pattern, and severity to `skills/secret-leak-check/references/checks.md`.
2. Add an allowlist note if the provider has public-by-design keys.
3. Add a fake fixture under `examples/vulnerable/` if the pattern needs a demo.
4. Test it locally (below).

Keep one pattern or behavior per pull request.

## Local testing

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

## Pull requests

- Explain the false-positive impact of a new pattern.
- Update the README or references when behavior changes.
- Keep fixtures fake.
