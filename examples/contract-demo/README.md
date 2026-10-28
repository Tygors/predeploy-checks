# Contract demo fixture

A static frontend/backend/env mismatch. No server, install, or network is needed.

## Files

- `frontend/api.js`: GET, POST, and DELETE calls.
- `backend/app.py`: GET and POST routes; no DELETE.
- `.env.example`: two declared vars, one stale flag.

## Ask your agent

> Check whether the frontend, backend, and environment agree in examples/contract-demo.

## Expected findings

- `BROKEN`: `DELETE /api/users/:id` has no DELETE route; the backend defines GET only (`frontend/api.js:17`, `backend/app.py:11`).
- `BROKEN`: `JWT_SECRET` is required by `backend/app.py:6` but not declared in `.env.example`.
- `DRIFT`: `UNUSED_FLAG` is declared in `.env.example:3` but used nowhere.
- `IN SYNC`: GET and POST routes match; `VITE_API_BASE` and `DATABASE_URL` are declared.

Expected verdict: `BROKEN`.

The fixture is static on purpose. The client and server never run, so the check has to read the code.
