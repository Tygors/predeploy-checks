# Report template

Keep the report short enough to read once. Put exactly one verdict line directly under the header.

Count used env vars in `<k> used env vars`; list declared-but-unused vars separately in the env table.

```text
CONTRACT CHECK - <scope> (<n> client calls, <m> server routes, <k> used env vars)
Verdict: <NO CONTRACT | BROKEN | DRIFT | IN SYNC>

Broken or drifting
| Item | What disagrees | Why it matters | Evidence |
|---|---|---|---|
| <call or variable> | <client vs server, or used vs declared> | <user impact> | <client file:line; server file:line> |

Matched
| Surface | Client | Server |
|---|---|---|
| <METHOD path> | <file:line> | <file:line> |

Env contract
| Variable | Used in | Declared in | Result |
|---|---|---|---|
| <NAME> | <file:line> | <file:line or none> | <IN SYNC / DRIFT / BROKEN> |

Contract tests
- `<command>` -> <passed / failed / not run> (<what it covers, or why it did not run>)

Fix first
1. <smallest route, client, or config change>
2. ...

Limits
- <what could not be resolved, sampled, or verified>
```

Omit the `Matched` table when it would be longer than the findings; summarize the count instead. Never omit a mismatch.

## Filled example

Audit of [`examples/contract-demo`](../../../examples/contract-demo/README.md). The client and server never run; the findings come from the files.

```text
CONTRACT CHECK - examples/contract-demo (3 client calls, 2 server routes, 3 used env vars)
Verdict: BROKEN

Broken or drifting
| Item | What disagrees | Why it matters | Evidence |
|---|---|---|---|
| DELETE /api/users/:param | client sends DELETE; server defines GET only | deleting a user returns 405 or 404 | frontend/api.js:17; backend/app.py:11 |
| JWT_SECRET | required by the backend, not declared | a fresh deploy fails at startup | backend/app.py:6; no declaration in config |
| UNUSED_FLAG | declared, used nowhere | stale config misleads deployment | .env.example:3 |

Matched
| Surface | Client | Server |
|---|---|---|
| GET /api/users/:param | frontend/api.js:4 | backend/app.py:11 |
| POST /api/users | frontend/api.js:9 | backend/app.py:16 |

Env contract
| Variable | Used in | Declared in | Result |
|---|---|---|---|
| VITE_API_BASE | frontend/api.js:1 | .env.example:1 | IN SYNC |
| DATABASE_URL | backend/app.py:5 | .env.example:2 | IN SYNC |
| JWT_SECRET | backend/app.py:6 | none | BROKEN |
| UNUSED_FLAG | none | .env.example:3 | DRIFT |

Contract tests
- none found; no OpenAPI schema or contract suite in the fixture.

Fix first
1. Add DELETE /api/users/{user_id} to backend/app.py, or remove the client call.
2. Add JWT_SECRET to .env.example and the deploy config.
3. Remove UNUSED_FLAG or wire it up.

Limits
- The base origin in frontend/api.js is a variable; paths were compared after stripping it.
- Response field compatibility was not checked; no OpenAPI schema or contract test exists.
```

This example matches the fixture so you can compare your own run. For another project, derive the rows from that project's files.

## Report rules

- Start with the verdict.
- List every mismatch; matched surfaces can be summarized.
- Cite both sides when both exist: client `file:line` and server `file:line`, or used and declared env locations. For a missing route or undeclared var, cite the existing side and say the other is absent.
- A fully dynamic URL is `DRIFT`, not `BROKEN`. Say what could not be resolved.
- A dynamic origin with a comparable literal path is a note, not `DRIFT`; still report whether the path matched.
- A call that matches only the OpenAPI spec, not the code, is `DRIFT`, not `BROKEN`.
- A var declared only in README or deploy docs is `DRIFT`, not `IN SYNC`.
- Do not report a backend route with no client as broken; it may be public.
- Do not report a public client env prefix as a secret.
- Do not claim response fields disagree without an OpenAPI/GraphQL schema or a contract test.
- Explain impact in plain language: "deleting a user returns 404", "a fresh deploy fails at startup".
- If a contract test ran, say what it covered. A pass is not proof for untested surfaces.
- If no contract test or schema exists, say so; do not imply field-level verification.
- If the repo has no client/server/env surfaces, use `Verdict: NO CONTRACT`.
- Never print secrets, tokens, personal data, or production data found in config files.
