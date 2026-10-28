# Preview demo fixture

A tiny server with a deliberately broken preview. No dependencies and no network.

## Run it

```bash
python examples/preview-demo/server.py 8000
```

Then ask your agent:

> Check http://localhost:8000 before I promote it.

Stop the server with `Ctrl+C`.

## Expected findings

- `/` returns 200, but `#root` is empty: visitors see a blank page.
- `/missing.js` returns 404: the only script never loads.
- `/boom` returns 500.
- `/not-found` returns 200 with a "This page could not be found" title.
- `/redirect` ends on `/login` (`Sign in`); verify the gate is expected.
- `/ok` returns 200 and renders a heading.

Expected verdict: `FAIL`.

Localhost uses HTTP, so the mixed-content check does not apply here.
