#!/usr/bin/env python3
"""Generate a deliberately leaky build output for demos and tests.

Every value in the generated output is fake. Do not use any of it.
The output goes to examples/vulnerable/dist/, which is ignored by git.
"""

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

# Built at runtime so the committed file never contains a complete key pattern.
FAKE_OPENAI = "sk-" + "proj-" + "FAKE" + "0" * 32


def b64url(value):
    raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def fake_jwt():
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"iss": "supabase", "role": "service_role", "ref": "demo"}
    return ".".join([b64url(header), b64url(payload), "fake-signature"])


def main():
    (DIST / "assets").mkdir(parents=True, exist_ok=True)

    (DIST / "index.html").write_text(
        '<!doctype html><html><body><div id="app"></div>'
        '<script src="/assets/app.js"></script></body></html>\n',
        encoding="utf-8",
    )

    (DIST / "assets" / "app.js").write_text(
        'const apiKey = "' + FAKE_OPENAI + '";\n'
        'const supabaseKey = "' + fake_jwt() + '";\n'
        '//# sourceMappingURL=app.js.map\n'
        'console.log("demo");\n',
        encoding="utf-8",
    )

    (DIST / "assets" / "app.js.map").write_text(
        json.dumps(
            {
                "version": 3,
                "file": "app.js",
                "sources": ["src/app.ts"],
                "sourcesContent": [
                    "export const apiKey = process.env.OPENAI_API_KEY;\n"
                ],
                "names": [],
                "mappings": "",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (DIST / ".env").write_text(
        "OPENAI_API_KEY=" + FAKE_OPENAI + "\n", encoding="utf-8"
    )

    print("Generated:", DIST)
    print("Scan the directory:", "examples/vulnerable/dist")
    print(
        "Or serve it:",
        'python -m http.server 8000 --directory "examples/vulnerable/dist"',
    )


if __name__ == "__main__":
    main()
