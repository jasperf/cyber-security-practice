#!/usr/bin/env python3
"""Lab 01 — HTTP by hand. Target control and self-marking checker.

    python3 lab.py start     # bring the target up on 127.0.0.1
    python3 lab.py status    # is it up, and on which port?
    python3 lab.py check     # answer the questions, get marked
    python3 lab.py stop      # shut it down

On Windows 11 use `py lab.py start` (or `python lab.py start`).
"""

from __future__ import annotations

import base64
import http.client
import os
import secrets
import sys

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(LAB_DIR), "lib"))

import labkit as kit  # noqa: E402

PREFERRED_PORT = 8081
LOG_PATH = os.path.join(LAB_DIR, "server.log")
STATE = kit.State(LAB_DIR)


# ------------------------------------------------------------------ start ----

def cmd_start() -> int:
    if os.path.exists(STATE.path):
        old = STATE.load()
        if kit.port_open(old["port"]):
            print(
                f"\nTarget already up on {kit.BOLD}127.0.0.1:{old['port']}{kit.RESET}. "
                f"Stop it first to reshuffle the flags.\n"
            )
            return 0
        STATE.clear()

    port = kit.free_port(PREFERRED_PORT)
    # Fresh every run: the flags exist only on the wire and in the server's
    # memory, so the only way to answer is to actually speak HTTP.
    flag1 = "CTF{http_%s}" % secrets.token_hex(6)
    flag2 = "CTF{basic_%s}" % secrets.token_hex(6)
    user = "labuser"
    password = secrets.token_hex(4)

    pid = kit.spawn(
        [
            sys.executable,
            os.path.join(LAB_DIR, "server.py"),
            "--port", str(port),
            "--flag1", flag1,
            "--flag2", flag2,
            "--user", user,
            "--password", password,
        ],
        LOG_PATH,
    )

    if not kit.wait_for_port(port):
        kit.kill(pid)
        print(f"\n{kit.BAD}Target failed to start.{kit.RESET} See {LOG_PATH}\n")
        return 1

    STATE.save(
        port=port,
        pid=pid,
        user=user,
        password=password,
        flag1_sha=kit.sha256(flag1),
        flag2_sha=kit.sha256(flag2),
        basic=base64.b64encode(f"{user}:{password}".encode()).decode(),
    )

    nc = kit.netcat_name()
    print(f"""
{kit.BOLD}{kit.ACC}Target up{kit.RESET} — {kit.BOLD}127.0.0.1:{port}{kit.RESET}  (pid {pid})

  Credentials for /secret : {kit.BOLD}{user}:{password}{kit.RESET}
  Request log             : {LOG_PATH}

  First request, if you want one to copy:

    {kit.CYAN}{nc} 127.0.0.1 {port}{kit.RESET}
    {kit.DIM}then type, ending with a blank line:{kit.RESET}
    {kit.CYAN}GET / HTTP/1.1{kit.RESET}
    {kit.CYAN}Host: 127.0.0.1{kit.RESET}
    {kit.CYAN}Connection: close{kit.RESET}

  Work through README.md, then: {kit.BOLD}{kit.python_cmd()} lab.py check{kit.RESET}
""")
    kit.advise(("nc", "ncat"))
    print()
    return 0


# ------------------------------------------------------------- stop/status ----

def cmd_stop() -> int:
    if not os.path.exists(STATE.path):
        print("\nNothing to stop — no target recorded.\n")
        return 0
    state = STATE.load()
    kit.kill(state["pid"])
    STATE.clear()
    print(f"\nTarget on port {state['port']} stopped. Flags for that run are gone.\n")
    return 0


def cmd_status() -> int:
    if not os.path.exists(STATE.path):
        print(f"\nTarget is {kit.BOLD}down{kit.RESET}. Start it: "
              f"{kit.BOLD}{kit.python_cmd()} lab.py start{kit.RESET}\n")
        return 1
    state = STATE.load()
    up = kit.port_open(state["port"])
    word = f"{kit.OK}up{kit.RESET}" if up else f"{kit.BAD}down (stale state){kit.RESET}"
    print(f"\nTarget is {word} on 127.0.0.1:{state['port']} (pid {state['pid']})")
    print(f"Credentials for /secret: {state['user']}:{state['password']}\n")
    return 0 if up else 1


# ------------------------------------------------------------------ check ----

def head_of(port: int, path: str, method: str = "GET") -> tuple[int, dict]:
    """Status and headers for one request — how the checker derives its answers.

    It asks the live target rather than hardcoding, so the marking cannot drift
    away from what the server on your machine actually said.
    """
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    try:
        conn.request(method, path)
        response = conn.getresponse()
        response.read()
        return response.status, dict(response.getheaders())
    finally:
        conn.close()


def cmd_check() -> int:
    state = STATE.load()
    port = state["port"]
    if not kit.port_open(port):
        print(f"\n{kit.BAD}Target is not answering on port {port}.{kit.RESET} "
              f"Run {kit.BOLD}{kit.python_cmd()} lab.py start{kit.RESET} again.\n")
        return 1

    _, flag_headers = head_of(port, "/flag.txt")
    flag_length = int(flag_headers["Content-Length"])

    lab = kit.Lab(
        "Lab 01 — HTTP by hand",
        f"Answer from what the target on 127.0.0.1:{port} actually sent you.",
    )

    lab.section("The request line and the response line")

    lab.ask_re(
        "What was the full status line the server replied with for `GET / HTTP/1.1`?",
        r"http/1\.1\s+200\s+ok",
        "HTTP/1.1 200 OK",
        "Version, code, reason phrase — in that order, on one line. The reason "
        "phrase is decorative; only the three-digit code is machine-read.",
        hint="Three parts, and the first one is not just 'HTTP'.",
    )

    lab.ask(
        "What is the value of the `Server:` response header?",
        "Tier1Lab/1.0",
        "Real servers leak build details here (nginx/1.24.0, Apache/2.4.58 "
        "with the OS). That is free reconnaissance for an attacker, which is "
        "why hardening guides tell you to flatten it.",
        hint="Look at the header block, not the body.",
    )

    lab.ask_num(
        "How many bytes did the server say the body of /flag.txt is "
        "(the `Content-Length` value)?",
        flag_length,
        why="Content-Length is how the client knows where the body ends on a "
            "keep-alive connection. Get it wrong and the next response is "
            "parsed as part of this one — that is HTTP request smuggling.",
        hint="It counts the trailing newline too.",
    )

    lab.section("Reading a body off the wire")

    lab.ask_sha(
        "What is the flag served at /flag.txt?",
        state["flag1_sha"],
        "The body starts after the blank line that ends the header block — "
        "CRLF CRLF. That blank line is the only thing separating headers from "
        "content.",
        hint="GET /flag.txt HTTP/1.1, with a Host header.",
        marks=2,
    )

    lab.section("Status codes that are not 200")

    lab.ask_num(
        "What status code comes back for a path that does not exist, e.g. /nope.txt?",
        404,
        why="4xx means the client asked for something wrong; 5xx means the "
            "server broke. 404 is specifically 'no such resource'.",
    )

    lab.ask_num(
        "What status code does /old-page return?",
        301,
        why="301 is a permanent redirect — browsers and search engines cache it "
            "hard. 302/307 are the temporary ones.",
        hint="It is a redirect, and it is the permanent kind.",
    )

    lab.ask(
        "Which response header carries the address a redirect points at, and what "
        "was its value? (answer as `Header: value`)",
        "Location: /new-page",
        "A redirect body is ignored — the whole message is in that one header. "
        "An open redirect, where an attacker controls this value, is a real "
        "vulnerability class.",
    )

    lab.section("Authentication, by hand")

    lab.ask_num(
        "What status code does /secret return with no credentials?",
        401,
        why="401 means 'unauthenticated — here is how to authenticate'. 403 "
            "means 'authenticated, but you still may not'. They are not "
            "interchangeable.",
    )

    lab.ask(
        "What realm does the `WWW-Authenticate` header name?",
        "tier1-lab",
        "The realm labels a protection space, so a client knows which stored "
        "credentials to reuse. It is the string a browser shows in the login box.",
        hint='It is quoted, right after `Basic realm=`.',
    )

    lab.ask(
        "What exact base64 string did you put in `Authorization: Basic ...`?",
        state["basic"],
        "Base64 is encoding, not encryption — anyone on the wire reverses it "
        "instantly. HTTP Basic is only safe inside TLS, and that is the whole "
        "reason HTTPS matters for logins.",
        hint="base64 of `user:password`. Encode it yourself; do not guess.",
    )

    lab.ask_sha(
        "What is the flag behind /secret?",
        state["flag2_sha"],
        "You just performed a complete authenticated HTTP transaction by hand, "
        "with no browser and no client library.",
        marks=2,
    )

    lab.section("Methods and the rules of HTTP/1.1")

    lab.ask_re(
        "How does the response to `HEAD /` differ from the response to `GET /`?",
        r"no body|without (a |the )?body|body is (omitted|absent)|headers only|"
        r"only (the )?headers|no content returned",
        "identical headers, no body",
        "HEAD is GET with the body suppressed — same status, same "
        "Content-Length. It is how you check size or existence cheaply, and "
        "how crawlers avoid downloading what they do not need.",
        hint="Compare the two responses line by line. Something is missing.",
    )

    lab.ask_num(
        "What status code do you get for an HTTP/1.1 request sent with no `Host:` "
        "header at all?",
        400,
        why="RFC 9112 §3.2 makes Host mandatory in HTTP/1.1. One IP can serve "
            "hundreds of sites, and Host is the only thing telling the server "
            "which one you want — so a request without it is unanswerable.",
        hint="It is a client error, and the most generic one there is.",
    )

    lab.finish()
    print(f"{kit.DIM}Target still running on port {port}. "
          f"Stop it with: {kit.python_cmd()} lab.py stop{kit.RESET}\n")
    return 0


# ------------------------------------------------------------------- main ----

COMMANDS = {"start": cmd_start, "stop": cmd_stop, "status": cmd_status, "check": cmd_check}


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action not in COMMANDS:
        print(__doc__)
        return 2
    return COMMANDS[action]()


if __name__ == "__main__":
    sys.exit(main())
