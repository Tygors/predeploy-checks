#!/usr/bin/env python3
"""Serve a deliberately broken preview for the preview-check demo."""

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGES = {
    "/": """<!doctype html>
<html><head><title>Preview demo</title></head>
<body>
<div id="root"></div>
<nav>
<a href="/ok">OK</a>
<a href="/not-found">Not found</a>
<a href="/redirect">Redirect</a>
<a href="/boom">Boom</a>
</nav>
<script src="/missing.js"></script>
</body></html>""",
    "/ok": """<!doctype html>
<html><head><title>Working page</title></head>
<body><main><h1>Working page</h1><p>This page rendered.</p></main></body></html>""",
    "/not-found": """<!doctype html>
<html><head><title>404: This page could not be found</title></head>
<body><h1>404</h1><p>This page could not be found.</p></body></html>""",
    "/login": """<!doctype html>
<html><head><title>Sign in</title></head>
<body><main><h1>Sign in</h1></main></body></html>""",
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="text/html; charset=utf-8", headers=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/redirect":
            self._send(302, "", headers={"Location": "/login"})
            return
        if path == "/boom":
            self._send(
                500,
                "<!doctype html><html><head><title>Internal Server Error</title></head>"
                "<body><h1>Internal Server Error</h1></body></html>",
            )
            return
        if path == "/missing.js":
            self._send(404, "not found", "text/plain; charset=utf-8")
            return
        if path in PAGES:
            self._send(200, PAGES[path])
            return
        self._send(
            404,
            "<!doctype html><html><head><title>Not Found</title></head>"
            "<body><h1>Not Found</h1></body></html>",
        )

    def do_HEAD(self):
        self.do_GET()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"preview demo on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
