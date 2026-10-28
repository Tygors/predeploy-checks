# Vulnerable demo fixture

This directory generates a deliberately leaky build output for demos and tests.
Every value in the generated output is fake. Do not use any of it.

## Generate

```bash
python examples/vulnerable/make_demo.py
```

This creates `examples/vulnerable/dist/` with:

- a fake OpenAI key in `assets/app.js`
- a fake Supabase `service_role` JWT in `assets/app.js`
- a public source map with `sourcesContent`
- a `.env` file at the web root

`dist/` and `.env` are ignored by git, so the generated secrets never enter the
repository.

## Scan it

Ask your agent:

> Check `./examples/vulnerable/dist` before I deploy.

Or serve it and scan the URL:

```bash
python -m http.server 8000 --directory examples/vulnerable/dist
```

Then scan `http://localhost:8000`.

## Expected findings

- red: OpenAI key in `assets/app.js`
- red: `service_role` JWT in `assets/app.js`
- red: source map with `sourcesContent`
- red: publicly readable `.env`
