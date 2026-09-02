#!/usr/bin/env python3
"""Your port scanner. Fill in the TODOs, then run it against the lab target.

    python3 scanner-template.py 9000 9100

The whole idea of a TCP connect scan fits in one sentence: try to complete a
handshake with every port in the range, and write down the ones that answer.
Everything else — threads, timeouts, output formatting — is decoration.
"""

import socket
import sys
import time


def is_open(host: str, port: int, timeout: float = 0.3) -> bool:
    """Return True if a TCP handshake with host:port succeeds.

    TODO 1 — make a TCP socket:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    TODO 2 — set a timeout on it, or a filtered port will hang you for a minute:
        sock.settimeout(timeout)

    TODO 3 — try to connect. connect_ex() returns 0 on success and an error
        number otherwise, which is nicer than catching exceptions:
        return sock.connect_ex((host, port)) == 0

    Remember to close the socket — a `with` block does it for you.
    """
    raise NotImplementedError("TODO: implement is_open()")


def scan(host: str, lo: int, hi: int) -> list:
    """Scan every port from lo to hi inclusive, return the open ones.

    TODO 4 — loop over range(lo, hi + 1) and collect the ports where
        is_open() came back True.

    TODO 5 (once it works) — time it, then try to make it faster with
        concurrent.futures.ThreadPoolExecutor and ~100 workers.

        Expect a surprise: on loopback the parallel version is no faster,
        because closed ports there RST instantly and there is no waiting to
        overlap. Add a `time.sleep(0.05)` inside is_open() to fake network
        latency and run both again — *that* gap is why nmap keeps hundreds of
        probes in flight on a real network.
    """
    raise NotImplementedError("TODO: implement scan()")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: %s <low-port> <high-port>" % sys.argv[0])
        return 2

    host = "127.0.0.1"          # loopback only — see ../../SCOPE.md
    lo, hi = int(sys.argv[1]), int(sys.argv[2])

    started = time.time()
    open_ports = scan(host, lo, hi)
    elapsed = time.time() - started

    print("scanned %d ports in %.2fs" % (hi - lo + 1, elapsed))
    for port in open_ports:
        print("  %d/tcp open" % port)
    if not open_ports:
        print("  no open ports found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
