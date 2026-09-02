#!/usr/bin/env python3
"""Tier 1 lab target: a handful of fake services on random loopback ports.

Each listener accepts a connection, sends one banner line, and hangs up —
which is exactly enough to be found by a TCP connect scan and to reward
banner grabbing. One of them hands out the flag.

Binds to 127.0.0.1 only. Started and stopped by lab.py; you should not need
to run this yourself.
"""

import argparse
import socket
import sys
import threading

# Deliberately imitating the shape of real service banners: a version string
# on a plate is what makes banner grabbing the first move of an engagement.
BANNERS = [
    "220 lab-ftp 1.2.3 ready\r\n",
    "SSH-2.0-LabSSH_1.0\r\n",
    "+OK lab-pop3 server ready\r\n",
    "LAB-ECHO service v0.3\r\n",
    "200 lab-smtp ESMTP ready\r\n",
]


def serve(port: int, banner: str, stop: threading.Event) -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind(("127.0.0.1", port))
    except OSError as exc:
        sys.stderr.write("could not bind %d: %s\n" % (port, exc))
        return
    listener.listen(8)
    listener.settimeout(0.5)
    sys.stderr.write("listening on 127.0.0.1:%d\n" % port)
    sys.stderr.flush()

    while not stop.is_set():
        try:
            conn, addr = listener.accept()
        except socket.timeout:
            continue
        except OSError:
            break
        try:
            conn.sendall(banner.encode())
            sys.stderr.write("connection on %d from %s\n" % (port, addr[0]))
            sys.stderr.flush()
        except OSError:
            pass
        finally:
            conn.close()
    listener.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ports", required=True, help="comma-separated port list")
    parser.add_argument("--flag", required=True)
    parser.add_argument("--flag-port", type=int, required=True)
    args = parser.parse_args()

    ports = [int(p) for p in args.ports.split(",")]
    stop = threading.Event()
    threads = []

    for index, port in enumerate(ports):
        if port == args.flag_port:
            banner = "LAB-VAULT 1.0 open — %s\r\n" % args.flag
        else:
            banner = BANNERS[index % len(BANNERS)]
        thread = threading.Thread(target=serve, args=(port, banner, stop), daemon=True)
        thread.start()
        threads.append(thread)

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        stop.set()


if __name__ == "__main__":
    main()
