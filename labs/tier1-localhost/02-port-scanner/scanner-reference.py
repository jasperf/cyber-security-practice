#!/usr/bin/env python3
"""Reference solution — open this only after your own version works.

Runs the scan twice, sequentially and then in parallel, and prints both times.

    python3 scanner-reference.py 9000 9100
    python3 scanner-reference.py 9000 9100 --banners
    python3 scanner-reference.py 9000 9100 --probe-delay 0.05

On loopback the two timings come out the same, and that is the lesson: closed
ports there answer with a RST immediately, so there is no waiting for
concurrency to hide. `--probe-delay` adds an artificial pause per probe to
stand in for network round-trip time and firewall timeouts. It is a
simulation, not a measurement of your network — but the gap it opens up is
exactly why nmap keeps hundreds of probes in flight.
"""

import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"          # loopback only — see ../../SCOPE.md
TIMEOUT = 0.3
WORKERS = 100
PROBE_DELAY = 0.0


def is_open(port: int) -> bool:
    """One TCP connect attempt. This is the entire scanning primitive."""
    if PROBE_DELAY:
        time.sleep(PROBE_DELAY)        # stand-in for network latency
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        # connect_ex returns 0 on success, an errno otherwise. A refused
        # connection (RST) is a *closed* port; a timeout is a filtered one.
        return sock.connect_ex((HOST, port)) == 0


def scan_sequential(lo: int, hi: int) -> list:
    return [port for port in range(lo, hi + 1) if is_open(port)]


def scan_parallel(lo: int, hi: int) -> list:
    ports = range(lo, hi + 1)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = pool.map(is_open, ports)
    return [port for port, open_ in zip(ports, results) if open_]


def grab_banner(port: int) -> str:
    """Connect, say nothing, and read whatever the service volunteers."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        try:
            sock.connect((HOST, port))
            return sock.recv(1024).decode("utf-8", "replace").strip()
        except OSError:
            return "(no banner)"


def main() -> int:
    global PROBE_DELAY

    args = sys.argv[1:]
    if "--probe-delay" in args:
        index = args.index("--probe-delay")
        PROBE_DELAY = float(args[index + 1])
        del args[index:index + 2]
    if len(args) < 2:
        print("usage: %s <low-port> <high-port> [--banners] [--probe-delay SECONDS]"
              % sys.argv[0])
        return 2

    lo, hi = int(args[0]), int(args[1])
    count = hi - lo + 1

    started = time.time()
    sequential = scan_sequential(lo, hi)
    seq_time = time.time() - started

    started = time.time()
    parallel = scan_parallel(lo, hi)
    par_time = time.time() - started

    label = " (with %.0fms simulated latency)" % (PROBE_DELAY * 1000) if PROBE_DELAY else ""
    print("sequential: %d ports in %6.2fs%s" % (count, seq_time, label))
    print("parallel:   %d ports in %6.2fs%s   %d workers"
          % (count, par_time, label, WORKERS))
    if par_time:
        print("speedup:    %.1fx" % (seq_time / par_time))
    if not PROBE_DELAY:
        print("\nSame time either way — on loopback nothing ever waits. Try again "
              "with --probe-delay 0.05.")
    print()

    for port in parallel:
        line = "  %d/tcp open" % port
        if "--banners" in args:
            line += "   %s" % grab_banner(port)
        print(line)

    if sequential != parallel:
        print("\nwarning: the two scans disagree — raise TIMEOUT or lower WORKERS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
