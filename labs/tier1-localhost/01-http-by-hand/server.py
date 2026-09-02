#!/usr/bin/env python3
"""Tier 1 lab target: a small, strict HTTP/1.1 server on 127.0.0.1.

Deliberately *not* `python3 -m http.server`. That one speaks HTTP/1.0, never
enforces the Host header, and has no auth or redirect routes — so half the
things worth learning by hand would never fire. This one:

  * speaks HTTP/1.1 with keep-alive
  * rejects an HTTP/1.1 request that has no Host header (400) — RFC 9112 s3.2
  * has a 301 redirect, a 401 Basic-auth route, and a 404 for everything else
  * always sends Content-Length, so you can see where a body starts and stops

Binds to 127.0.0.1 only. Started and stopped by ./target.sh — you should not
need to run it yourself.
"""

import argparse
import base64
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SERVER_NAME = "Tier1Lab/1.0"
REALM = "tier1-lab"

# Filled in from argv by main(); the flags are regenerated on every start,
# so they exist only on the wire and in this process's memory.
CONF = {"flag1": "", "flag2": "", "user": "", "password": ""}

INDEX = """<!doctype html>
<title>Tier 1 lab target</title>
<h1>Tier 1 lab target</h1>
<ul>
  <li>/flag.txt   &mdash; plain text</li>
  <li>/old-page   &mdash; moved</li>
  <li>/new-page   &mdash; where it moved to</li>
  <li>/secret     &mdash; needs credentials</li>
</ul>
"""

NEW_PAGE = "You found the new location.\n"


class LabHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # Stable Server header — the default leaks the Python version, which would
    # make the answer differ from machine to machine.
    def version_string(self):
        return SERVER_NAME

    # BaseHTTPRequestHandler logs to stderr; target.sh redirects that to
    # server.log so you can watch your own requests land.
    def log_message(self, fmt, *args):
        sys.stderr.write("%s  %s\n" % (self.log_date_time_string(), fmt % args))

    # -- helpers ------------------------------------------------------------

    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        # A HEAD response carries the headers of the equivalent GET but no body.
        if self.command != "HEAD" and body:
            self.wfile.write(body)

    def _authorised(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            raw = base64.b64decode(header[6:].strip()).decode("utf-8")
        except Exception:
            return False
        return raw == "%s:%s" % (CONF["user"], CONF["password"])

    # -- routing ------------------------------------------------------------

    def _handle(self):
        # RFC 9112 s3.2: an HTTP/1.1 request without Host is a 400. Nearly every
        # real server enforces this; it is why virtual hosting works at all.
        if self.request_version == "HTTP/1.1" and "Host" not in self.headers:
            self._send(400, b"Missing Host header (HTTP/1.1 requires one)\n")
            return

        path = self.path.split("?", 1)[0].rstrip("/") or "/"

        if path == "/":
            self._send(200, INDEX.encode(), "text/html; charset=utf-8")
        elif path == "/flag.txt":
            self._send(200, (CONF["flag1"] + "\n").encode())
        elif path == "/old-page":
            self._send(301, b"Moved.\n", extra={"Location": "/new-page"})
        elif path == "/new-page":
            self._send(200, NEW_PAGE.encode())
        elif path == "/secret":
            if self._authorised():
                self._send(200, (CONF["flag2"] + "\n").encode())
            else:
                self._send(
                    401,
                    b"Credentials required.\n",
                    extra={"WWW-Authenticate": 'Basic realm="%s"' % REALM},
                )
        else:
            self._send(404, b"Not found.\n")

    do_GET = _handle
    do_HEAD = _handle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--flag1", required=True)
    parser.add_argument("--flag2", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    CONF.update(
        flag1=args.flag1, flag2=args.flag2, user=args.user, password=args.password
    )

    server = ThreadingHTTPServer(("127.0.0.1", args.port), LabHandler)
    sys.stderr.write("target listening on 127.0.0.1:%d\n" % args.port)
    sys.stderr.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
