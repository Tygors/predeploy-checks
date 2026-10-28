# Report template

Keep the report short enough to read once. Put exactly one verdict line directly under the header.

Count pages as distinct checked URLs; a redirect is one page. Count assets as distinct script and stylesheet URLs, including assets that return 404. Images, fonts, and lazy-loaded assets are not counted.

```text
PREVIEW CHECK - <origin> (<n> pages, <m> assets)
Verdict: <FAIL | WARN | PASS>

Findings
| Page | Check | What happened | Why it matters |
|---|---|---|---|
| <path> | <HTTP / render / asset / mixed content / redirect> | <observed result> | <user impact> |

Passed
- <what was verified>

Fix first
1. <smallest fix>
2. ...

Limits
- <what was not checked or could not be verified>
```

## Filled example

Check of [`examples/preview-demo`](../../../examples/preview-demo/README.md) at `http://localhost:8000`. The server returns 200 for the homepage, but the app does not mount.

```text
PREVIEW CHECK - http://localhost:8000 (5 pages, 1 asset)
Verdict: FAIL

Findings
| Page | Check | What happened | Why it matters |
|---|---|---|---|
| / | render | #root is empty | visitors see no main content |
| / | asset | /missing.js returned 404 | the only script never loads |
| /boom | HTTP | returned 500 | the route crashes |
| /not-found | render | 200 with "This page could not be found" | a broken route looks live |
| /redirect -> /login | redirect | ends on Sign in | verify the gate is expected |

Passed
- /ok returned 200 and rendered a heading.

Fix first
1. Serve the homepage script so #root mounts.
2. Fix /boom or remove the link.
3. Return a real 404 for unknown routes instead of the error page with 200.

Limits
- Console and network errors were not captured.
- No login, form, or interactive flow was tested.
- Images, fonts, lazy-loaded assets, and external assets were not checked.
```

## Report rules

- Put the verdict directly under the header.
- Cite the page path and the check. This is a runtime check, so there is no source line to cite.
- Explain impact in plain language: "visitors see no main content", "the only script never loads". Say "empty app root" or "blank main content" when nav or other text remains; reserve "blank page" for a body with nothing visible.
- Do not list every passed asset; summarize.
- A 401/403 is a protected preview, not proof of a broken app; say so.
- A login redirect may be expected; mark it `WARN` and ask the user to confirm.
- Do not claim console, network, or interactive checks unless they were captured.
- If Chrome was unavailable, say rendering was not verified and do not return `PASS` on HTTP alone.
- Never print secrets, tokens, personal data, or query strings that may contain them.
