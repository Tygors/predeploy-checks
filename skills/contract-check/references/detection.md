# Detecting contracts

## Server routes

Record method, normalized path, and `file:line` for every route you can resolve.

### Flask

```python
@app.route("/api/users/<int:user_id>", methods=["GET"])
@app.get("/api/users/<int:user_id>")
@bp.post("/api/users")
```

A route without `methods` accepts `GET` only.

### FastAPI

```python
@app.get("/api/users/{user_id}")
@router.post("/api/users")
@app.api_route("/api/health", methods=["GET", "HEAD"])
```

### Express

```js
app.get("/api/users/:id", handler)
router.post("/api/users", handler)
app.route("/api/users/:id").get(handler).delete(handler)
app.use("/api", router)
```

Resolve a literal mount prefix such as `app.use("/api", router)`. If the prefix is dynamic, mark the route unresolved.

### Next.js App Router

A file at `app/api/users/[id]/route.ts` exports `GET`, `POST`, `PUT`, `PATCH`, or `DELETE`. The path is `/api/users/:param` with the method from the export.

### Next.js Pages Router

`pages/api/users/[id].ts` usually reads `req.method` in a switch. Record only the methods you can see handled.

### Django

```python
path("api/users/<int:user_id>/", view)
re_path(r"^api/users/(?P<id>\d+)/$", view)
```

Include the project URL prefix when it is a literal.

### OpenAPI / Swagger

Read `paths` and the method keys under each path. Treat the spec as a claim; compare it with the code routes.

## Client calls

### fetch

```js
fetch("/api/users")
fetch(`${API_BASE}/api/users/${id}`)
fetch("/api/users", { method: "POST", body })
```

Default to `GET` only when the `method` option is absent. Do not assume `POST` from a body alone.

### axios and similar

```js
axios.get("/api/users")
axios.post("/api/users", body)
axios({ url: "/api/users", method: "DELETE" })
ky.get("/api/users")
useSWR("/api/users")
```

For an instance with `baseURL: "/api"`, resolve `client.get("/users")` to `/api/users` only when the base URL is literal. Otherwise mark it unresolved.

### Out of scope

- GraphQL operations and generated clients
- tRPC, Supabase, Firebase, and other SDK calls that do not expose REST paths
- external origins
- server-to-server calls outside the compared roots

Mark them unresolved; do not invent a path.

An external origin is out of scope. A dynamic base that points at the same backend is different: strip the base, compare the literal path, and note that the origin was unresolved. If the base could point at another service, mark the call unresolved.

## Path normalization

1. Drop the origin and query string.
2. Drop a trailing slash unless the path is `/`.
3. Replace every parameter form with `:param`: `:id`, `{id}`, `<int:id>`, `[id]`, `${id}`.
4. Preserve case.
5. Resolve a literal base prefix when you can.

| Source | Normalized |
|---|---|
| `/api/users/${id}` | `/api/users/:param` |
| `/api/users/{user_id}` | `/api/users/:param` |
| `/api/users/<int:user_id>` | `/api/users/:param` |
| `app/api/users/[id]/route.ts` | `/api/users/:param` |
| `/api/users/` | `/api/users` |

A path built from a variable (`"/api/" + resource`) is unresolved. If a template literal starts with an unresolved base (`${API_BASE}/api/users/${id}`), strip the leading variable and compare the remaining literal path (`/api/users/:param`); note that the origin/base was not resolved. A path with a different literal version prefix (`/v2` vs `/v1`) is a real mismatch.

## Environment variables

### Usage patterns

- `process.env.NAME`, `process.env["NAME"]`
- `import.meta.env.NAME`
- `os.environ["NAME"]` (required)
- `os.environ.get("NAME")` (required unless a default is passed; it returns `None` otherwise)
- `os.getenv("NAME", "default")` (optional)
- `Deno.env.get("NAME")`, `Bun.env.NAME`

A JS access with an adjacent fallback (`process.env.X || "..."`, `process.env.X ?? "..."`) is optional. A bare `process.env.X` or `import.meta.env.X` is required.

### Declaration locations

- `.env.example`, `.env.sample`, `.env.template`, `.env.defaults`
- Dockerfile `ENV`, `docker-compose.yml` / `compose.yaml` `environment`
- CI workflow `env`
- `vercel.json`, `netlify.toml`, `fly.toml`, `render.yaml`
- README or deployment docs (weaker evidence; a docs-only declaration is `DRIFT`, not `IN SYNC`)

Do not read `.env` itself into the report. It may contain real secrets; only confirm whether a key exists.

### Public client prefixes

These are expected in the browser bundle and are not secret leaks:

- `VITE_`
- `NEXT_PUBLIC_`
- `REACT_APP_`
- `PUBLIC_` (SvelteKit)
- `NUXT_PUBLIC_`
- `EXPO_PUBLIC_`

Their presence is a contract concern, not a `secret-leak-check` finding.

### Runtime names to ignore

`NODE_ENV`, `MODE`, `DEV`, `PROD`, `SSR`, `BASE_URL`, `PATH`, `HOME`, `PWD`, `SHELL`, `USER`, `TZ`, `LANG`, `CI`, `PORT` (when the platform provides it). Note a project-owned exception instead of flagging the name blindly.

## Contract tests

Look for a documented command or dependency:

- JavaScript: `test:contract`, Jest/Vitest with OpenAPI validators, Dredd, Pact
- Python: `schemathesis`, `pact-python`, `openapi-core`, `pytest` contract suites
- OpenAPI diff tools

Run only the documented command, and only if it is safe locally. Ask before starting servers, databases, or credential-dependent suites. A pass covers only the tested surfaces.

## False-positive rules

- Do not report a missing route when the client URL is dynamic. Report `DRIFT` and name the unresolved expression.
- A path that exists with a different method is a method mismatch, not a missing path. Cite the route that exists and name the method it supports.
- Do not flag a backend route just because no client calls it; it may be public or consumed elsewhere.
- Do not treat `/api/users/:id` and `/api/users/:param` as different; both normalize to `:param`.
- Do not ignore API version prefixes.
- Do not treat a framework-generated auth route (NextAuth, Supabase) as missing.
- Do not report a public client env prefix as a leaked secret.
- Do not claim response fields disagree without a schema or contract test.
- If a literal trailing slash is required by the server, note it as a normalization risk instead of `BROKEN`.

## Plain-language impact

Use the user-visible failure, not the internal label:

- "Deleting a user will return 404 because the server has no DELETE route."
- "A fresh deploy will fail at startup because JWT_SECRET is used but never declared."
- "The client calls `/api/v2/users`, but the server only defines `/api/v1/users`."
