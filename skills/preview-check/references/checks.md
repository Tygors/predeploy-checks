# Preview checks

## Chrome detection

Set `CHROME` before rendering:

```bash
CHROME=""
for c in \
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "$(command -v google-chrome 2>/dev/null)" \
  "$(command -v chromium 2>/dev/null)" \
  "$(command -v chromium-browser 2>/dev/null)"; do
  if [ -n "$c" ] && [ -x "$c" ]; then CHROME="$c"; break; fi
done
```

If `CHROME` is empty, do HTTP-only checks and report that rendering was not verified.

## HTTP responses

```bash
origin="$(printf '%s' "$URL" | sed -E 's#(https?://[^/]+).*#\1#')"
tmp="$(mktemp -d)"
# First response, without following redirects.
curl -sS -o /dev/null --max-time 15 \
  -w '%{http_code}\t%{redirect_url}\n' "$URL"
# Final response after up to 5 redirects.
curl -sS -L --max-time 15 --max-redirs 5 -o "$tmp/page.html" \
  -w '%{http_code}\t%{url_effective}\t%{content_type}\n' "$URL"
```

`curl -L` hides the first 302 in `url_effective`; record the redirect target separately.

Map curl failures:

- exit 6: host not found -> `FAIL`
- exit 7: connection refused -> `FAIL`
- exit 28: timeout -> `FAIL` or `WARN` if the preview is known to cold-start; say which
- exit 47: too many redirects -> `FAIL`

Status handling:

| Status | Critical page | Secondary page |
|---|---|---|
| 200 | check content | check content |
| 301/302 to login | `WARN` | `WARN` |
| 401/403 | `WARN` auth gate | `WARN` |
| 404 | `FAIL` | `WARN` |
| 5xx | `FAIL` | `FAIL` |
| JSON body | `WARN` | `WARN` |

Any 5xx on any checked page is `FAIL`.

A redirect loop is `FAIL`. A final URL on a login path is `WARN`; verify it is expected.

## Same-origin rules

Use the origin of the URL the user named. A link or asset is in scope when:

- it starts with `/` and resolves to the same origin
- it starts with the same `https://host` or `http://host`
- it uses `//host/...` with the same host

Skip `#`, `mailto:`, `tel:`, `javascript:`, `data:`, and other origins. Do not crawl external links.

Relative URLs such as `assets/app.js` need base resolution. If you cannot resolve them reliably, skip them and say so.

## Pages

Extract same-origin links from the rendered homepage:

```bash
grep -oE '<a[^>]+href="[^"]+"' "$tmp/dom.html" \
  | sed -E 's/.*href="([^"]+)".*/\1/' \
  | sort -u
```

Take the homepage plus user-named routes first, then same-origin links until 10 pages total, including the homepage. A redirect counts as one page; do not add its final URL as a second page. Do not treat an API path as a page.

## Assets

Scripts:

```bash
grep -oE '<script[^>]+src="[^"]+"' "$tmp/dom.html" \
  | sed -E 's/.*src="([^"]+)".*/\1/'
```

Stylesheets:

```bash
grep -oE '<link[^>]+href="[^"]+\.css[^"]*"' "$tmp/dom.html" \
  | sed -E 's/.*href="([^"]+)".*/\1/'
```

Check at most 30 same-origin, resolvable script and stylesheet URLs total. Extract assets from the homepage and user-named critical pages; secondary-page assets are out of scope. Count an asset when you request it, even if it returns 404. A missing script or stylesheet on a critical page is `FAIL`.

## Rendering

```bash
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --virtual-time-budget=5000 --dump-dom "$URL" > "$tmp/dom.html" 2> "$tmp/chrome.log"
```

If `--headless=new` fails on an older Chrome, try `--headless` once. If Chrome still fails, do not claim render success; use `WARN`.

Before any blank or empty-root finding, retry once with `--virtual-time-budget=10000`; client rendering can be slower than the first budget. A non-empty shell with no meaningful content is not detected; report that as a limit.

### Empty root

```bash
grep -qE '<div id="(root|app|__next|___gatsby)"[^>]*>[[:space:]]*</div>' "$tmp/dom.html"
```

Also check for an empty `<main>`. A match means the app mounted nothing: `FAIL` on a critical page, `WARN` on a secondary page.

### Error markers

```bash
grep -qiE 'Failed to compile|Build Error|Module not found|Unhandled Runtime Error|Application error: a client-side exception|Internal Server Error|This page could not be found|404: This page could not be found' "$tmp/dom.html"
```

Confirm the marker is visible content or an error overlay, not a code sample or a string in documentation.

### Title

```bash
grep -oE '<title>[^<]*</title>' "$tmp/dom.html"
```

An empty title, `Error`, or a framework error title on a critical page is `WARN`; combine it with the body checks.

### Mixed content

Only when the final page URL is `https`:

```bash
grep -oiE '<(script|link|img|iframe|source)[^>]+(src|href)="http://[^"]+' "$tmp/dom.html"
```

A match is `FAIL` on a critical HTTPS page and `WARN` on a secondary page; browsers block or degrade these resources. A `http://` link in visible text is not mixed content.

## Console and network

`--dump-dom` does not expose console errors or failed network requests. Do not claim them.

If the agent has a browser tool that captures console or network events, it may use it and must say which checks it ran. Otherwise list this as a limit.

## False positives

- An unknown route returning the SPA shell with 200 is not automatically fine; look for a 404 title or error marker.
- A 401/403 can be preview password protection, not a broken app.
- A login redirect can be the intended behavior.
- A missing external CDN asset is out of scope; report it as external and unchecked.
- Lazy-loaded content may not appear within the virtual time budget; retry once with a larger budget before calling it blank.
- An error string in a docs page or code sample is not an error overlay.
- A `/favicon.ico` 404 is not a preview failure; do not check it.
- Localhost over HTTP is not a mixed-content situation.
- If the user identifies a page as their intentional 404 page, note it and do not treat the 200-with-404 content as a failure.
- A non-empty shell with no meaningful content is not detected; say so instead of calling it clean.

## What is not a finding

- Slow performance within the timeout.
- Missing SEO or social tags.
- Console warnings that were not captured.
- Broken external links.
- Visual differences from a design file.
