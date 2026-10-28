---
name: preview-check
description: Check a preview deployment before promoting it to production. Use after a preview deploy or when the user asks whether a preview URL actually works. Verifies routes, rendered content, error pages, assets, and mixed content with curl and headless Chrome, and reports FAIL / WARN / PASS.
---

# Preview Check

A preview URL returning 200 is not proof that the app works. The page can render blank, the build can show an error overlay, the main script can 404, or an HTTPS page can load an insecure resource. Preview is the last place to catch these before production.

This skill answers one question: **does the preview actually work before I promote it?**

It checks only the origin the user names. It does not log in, click through flows, or submit forms. Written for people who may not read code fluently.

## When to use

- After a preview deploy, before promoting to production.
- The user gives a preview URL and asks whether it is safe to promote.
- A build was deployed but the page looks blank or broken.
- After changing routing, bundling, or asset paths.
- Before a demo or launch.

## Rules

- Scan only the origin the user names. Same-origin links only; do not crawl other domains.
- GET and HEAD only. Do not submit forms, click buttons, log in, or mutate data.
- Limit to 10 pages total and 30 assets total. Use a 15 second timeout per request. Redirect hops do not count as separate pages.
- Read-only. Never upload results.
- Use headless Chrome for rendering. If Chrome is unavailable, do HTTP checks only and say so.
- Do not claim console, network, or interactive checks unless you actually captured them.
- A 401 or 403 can be a protected preview, not a failure. Report it as a warn with the reason.
- Match the user's language in the report.

## Step 1: Define the target

Normalize the URL and keep its origin. Stop if the scheme is not `http` or `https`.

- If the user names critical routes, check those first.
- Otherwise use the homepage plus same-origin links found on it, up to 10 pages total, including the homepage.
- Critical pages are the homepage and routes the user names. Auto-discovered links are secondary.
- For localhost, HTTPS and mixed-content checks do not apply; say so.
- Do not follow links to other origins.

## Step 2: Check HTTP responses

For each page, record the first response (status and redirect target) and the final response after up to 5 redirects. Also record the content type.

- Homepage or user-named route: 4xx is `FAIL`, except 401/403 which is a `WARN` auth gate.
- Any 5xx on any checked page is `FAIL`.
- Auto-discovered secondary route with 4xx is `WARN`.
- A redirect to a login path (`/login`, `/signin`, `/auth`) is `WARN`; verify it is expected.
- A redirect loop is `FAIL`.
- A page that returns JSON instead of HTML is `WARN`; the preview may be serving an API error.
- HTTP for a non-localhost preview is `WARN`; secure cookies and APIs may fail.

## Step 3: Check assets

From the rendered homepage and user-named critical pages, extract same-origin `script src` and stylesheet `href` URLs. Secondary-page assets are out of scope. Check up to 30 assets total.

- A missing script or stylesheet on a critical page is `FAIL`; the page may render blank or unstyled.
- External assets, images, fonts, and lazy-loaded assets are out of scope; say they were not checked.
- Inline scripts and `data:` URLs are not assets.

## Step 4: Check what renders

Detect Chrome and dump the rendered DOM after a short virtual time budget:

```bash
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --virtual-time-budget=5000 --dump-dom "$URL" > "$tmp/dom.html" 2> "$tmp/chrome.log"
```

Check the DOM for:

- an empty app root such as `#root`, `#app`, `#__next`, `#___gatsby`, or an empty `<main>`
- build or runtime error text: `Failed to compile`, `Build Error`, `Module not found`, `Unhandled Runtime Error`, `Application error: a client-side exception`, `Internal Server Error`, `This page could not be found`, `404: This page could not be found`
- an empty or error title
- mixed content when the final page is HTTPS: a `script`, `link`, `img`, `iframe`, or `source` with an `http://` URL

Before any blank or empty-root finding, retry once with `--virtual-time-budget=10000`.

A blank root or error overlay is `FAIL` on a critical page and `WARN` on a secondary page. Mixed content is `FAIL` on a critical HTTPS page and `WARN` on a secondary page. If the homepage has the same error, the homepage `FAIL` already controls the verdict.

A non-empty but meaningless shell is not detected. State that limit instead of calling it clean.

If Chrome is unavailable, skip this step and make the limitation explicit. Do not infer render success from a 200.

## Step 5: Decide the verdict

Choose the first verdict that matches:

1. `Verdict: FAIL` - the origin is unreachable; a critical page is 4xx except 401/403; any checked page is 5xx; a critical page is blank or shows an error; a critical script or stylesheet is missing; a critical HTTPS page loads mixed content; or a redirect loop occurs.
2. `Verdict: WARN` - a protected preview returns 401/403; a login redirect is unexpected but not proven broken; a secondary page is 4xx; a page returns JSON instead of HTML; a secondary page is blank, shows an error, or loads mixed content; the preview is HTTP; or rendering could not be checked.
3. `Verdict: PASS` - every checked page returns 200, renders content, loads critical assets, and has no error marker or mixed content.

A single `FAIL` makes the verdict `FAIL`.

## Step 6: Report

Use `references/report.md`. Put the verdict directly under the header. Explain impact in plain language:

> The homepage renders an empty root, so a visitor sees a blank page even though the server returns 200.

List the smallest fixes first. Do not suggest a fix for a limitation you did not verify.

## Step 7: Re-check after fixes

Re-run only the affected page and asset checks, then update the verdict.

## Limits

- No clicks, forms, login, checkout, or authenticated flows.
- Console errors and failed network requests are not captured without a browser driver; say so.
- No visual regression, performance, SEO, or accessibility audit.
- Images, fonts, lazy-loaded assets, external links, and external assets are not checked.
- A non-empty shell with no meaningful content is not detected.
- A preview environment can differ from production config; this is not a production monitor.
- This is not a replacement for end-to-end tests.
