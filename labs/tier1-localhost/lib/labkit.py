#!/usr/bin/env python3
"""labkit — shared machinery for the Tier 1 labs.

Same self-marking philosophy as the HTML sheets: you answer, it marks, it
explains. Nothing is uploaded, nothing is tracked, no account, no server.

Written in Python rather than shell so the labs run unchanged on macOS, Linux
and Windows 11 — a `.sh` checker would have needed WSL or Git Bash just to
mark an answer. Standard library only: no pip install, ever.

Not run directly; imported by each lab's `lab.py`.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time

IS_WINDOWS = os.name == "nt"


# --------------------------------------------------------------- colour ----

def _colour_enabled() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    if IS_WINDOWS:
        # Windows Terminal and PowerShell 7 handle ANSI once virtual-terminal
        # processing is on; the old conhost does not, so fail closed.
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            # -11 = STD_OUTPUT_HANDLE, 0x4 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                return False
            return bool(kernel32.SetConsoleMode(handle, mode.value | 0x4))
        except Exception:
            return False
    return True


if _colour_enabled():
    RESET, DIM, BOLD = "\033[0m", "\033[2m", "\033[1m"
    OK, BAD, ACC, CYAN = "\033[32m", "\033[31m", "\033[33m", "\033[36m"
else:
    RESET = DIM = BOLD = OK = BAD = ACC = CYAN = ""

RULE = "-" * 60


# -------------------------------------------------------------- helpers ----

def sha256(text: str) -> str:
    """Hex digest of a string, so flags never sit in plaintext in a lab file."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalise(text: str) -> str:
    """Lowercase, collapse whitespace, trim — for forgiving text comparison."""
    return re.sub(r"\s+", " ", text).strip().lower()


def normalise_set(text: str) -> list[int]:
    """'9004, 9001 9009' and '9009,9001,9004' both become [9001, 9004, 9009]."""
    return sorted({int(n) for n in re.findall(r"\d+", text)})


def advise(*requirements) -> None:
    """Warn about tools the brief needs but this machine does not have.

    A requirement is a command name, or a tuple of interchangeable ones
    ("nc", "ncat") where having either is enough. Deliberately a warning and
    not a hard stop: the target still runs, and most steps have a fallback —
    you just want to know before you hit the step that needs it.
    """
    missing = []
    for requirement in requirements:
        names = requirement if isinstance(requirement, tuple) else (requirement,)
        if not any(shutil.which(name) for name in names):
            missing.append(names)
    if not missing:
        return

    print(f"\n  {ACC}{BOLD}Heads up — not on this machine:{RESET}")
    for names in missing:
        print(f"    {BOLD}{' or '.join(names)}{RESET}")
        hint = next((INSTALL_HINTS[n] for n in names if n in INSTALL_HINTS), None)
        if hint:
            print(f"      {DIM}{hint}{RESET}")


INSTALL_HINTS = {
    "nmap": (
        "macOS `brew install nmap` · Debian/Ubuntu `sudo apt install nmap` · "
        "Windows: installer at nmap.org/download (tick 'Add to PATH')"
    ),
    "nc": (
        "macOS/Linux: preinstalled. Windows: the Nmap installer ships `ncat`, "
        "which is the same idea — use `ncat` wherever the brief says `nc`."
    ),
    "ncat": "Ships with the Nmap installer — nmap.org/download",
    "dig": (
        "macOS/Linux: preinstalled. Windows: `winget install ISC.BIND` or use "
        "`Resolve-DnsName` in PowerShell."
    ),
}


def netcat_name() -> str:
    """Whichever netcat this machine actually has: nc, or ncat on Windows."""
    for candidate in ("nc", "ncat"):
        if shutil.which(candidate):
            return candidate
    return "nc"


def port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """Is something listening? Plain TCP connect — the same thing nmap -sT does."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def scan_range(lo: int, hi: int, workers: int = 100) -> list[int]:
    """Every open port in a range — the checker's own view of the target.

    Derived live rather than assumed, because the lab is not the only thing
    listening on your machine: whatever range we pick, some of the student's
    own services may already sit inside it.
    """
    from concurrent.futures import ThreadPoolExecutor

    ports = list(range(lo, hi + 1))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(port_open, ports))
    return [port for port, is_open in zip(ports, results) if is_open]


def free_port(preferred: int = 0) -> int:
    """A port nothing is using: the preferred one if it is free, else any."""
    if preferred and not port_open(preferred):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", preferred))
                return preferred
            except OSError:
                pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


# ---------------------------------------------------------------- state ----

class State:
    """The bit of shared memory between `start` and `check`.

    Holds the port, the child PID, and the *hashes* of this run's flags — so
    the checker can mark an answer it has never seen in plaintext. Written to
    .lab-state next to the lab, and gitignored: every start reshuffles it.
    """

    def __init__(self, lab_dir: str):
        self.path = os.path.join(lab_dir, ".lab-state")

    def save(self, **data) -> None:
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def load(self) -> dict:
        if not os.path.exists(self.path):
            print(
                f"\n{BAD}{BOLD}The target is not running.{RESET}\n"
                f"Start it first:  {BOLD}{python_cmd()} lab.py start{RESET}\n"
            )
            sys.exit(1)
        with open(self.path, encoding="utf-8") as handle:
            return json.load(handle)

    def clear(self) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)


def python_cmd() -> str:
    """How to spell "python" on this machine, for copy-pasteable messages."""
    return "py" if IS_WINDOWS else "python3"


# ---------------------------------------------------- process management ----

def spawn(args: list[str], log_path: str) -> int:
    """Start a detached background target, its stderr tee'd into a log file.

    The log is half the point: you can `tail -f` it (or `Get-Content -Wait` on
    Windows) in a second pane and watch your own hand-typed requests land.
    """
    log = open(log_path, "ab", buffering=0)
    kwargs: dict = {"stdout": log, "stderr": log, "stdin": subprocess.DEVNULL}
    if IS_WINDOWS:
        # No process group signalling on Windows; detach so closing the shell
        # does not take the target with it.
        kwargs["creationflags"] = 0x00000008 | 0x00000200  # DETACHED | NEW_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(args, **kwargs).pid


def kill(pid: int) -> bool:
    """Stop a target started by spawn(). True if we believe it is now gone."""
    try:
        if IS_WINDOWS:
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/F", "/T"],
                capture_output=True,
            )
            return result.returncode == 0
        os.kill(pid, signal.SIGTERM)
        for _ in range(20):
            time.sleep(0.05)
            try:
                os.kill(pid, 0)
            except OSError:
                return True
        os.kill(pid, signal.SIGKILL)
        return True
    except (OSError, ProcessLookupError):
        return False


def wait_for_port(port: int, timeout: float = 5.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_open(port):
            return True
        time.sleep(0.1)
    return False


# ------------------------------------------------------------- the quiz ----

class Lab:
    """An interactive, self-marking question run."""

    def __init__(self, title: str, subtitle: str = ""):
        self.n = 0
        self.score = 0
        self.total = 0
        self.missed: list[int] = []
        print(f"\n{BOLD}{ACC}{title}{RESET}")
        if subtitle:
            print(f"{DIM}{subtitle}{RESET}")
        print(f"{DIM}{RULE}{RESET}")
        print(
            f"{DIM}Type {BOLD}?{RESET}{DIM} for a hint, "
            f"{BOLD}skip{RESET}{DIM} to give up on a question.{RESET}"
        )

    # -- prompting ----------------------------------------------------------

    def _prompt(self, question: str, hint: str | None) -> str:
        self.n += 1
        print(f"\n{BOLD}{self.n:2d}.{RESET} {question}")
        while True:
            try:
                reply = input(f"    {ACC}>{RESET} ")
            except (EOFError, KeyboardInterrupt):
                print()
                return "skip"
            if reply.strip().lower() in ("?", "hint"):
                print(f"    {DIM}hint: {hint or 'no hint for this one'}{RESET}")
                continue
            return reply

    def _mark(self, correct: bool, marks: int, expected: str, why: str) -> None:
        self.total += marks
        if correct:
            self.score += marks
            print(f"    {OK}{BOLD}✓ correct{RESET} {DIM}(+{marks}){RESET}")
        else:
            self.missed.append(self.n)
            print(
                f"    {BAD}{BOLD}✗ not quite{RESET} — expected: "
                f"{BOLD}{expected}{RESET}"
            )
        if why:
            print(f"    {DIM}{why}{RESET}")

    # -- question types -----------------------------------------------------

    def ask(self, question, expected, why="", hint=None, marks=1):
        """Free text, compared case- and whitespace-insensitively."""
        reply = self._prompt(question, hint)
        self._mark(normalise(reply) == normalise(expected), marks, expected, why)

    def ask_num(self, question, expected, why="", tol=0, hint=None, marks=1):
        """A number, with optional tolerance (for timings and the like)."""
        reply = self._prompt(question, hint)
        found = re.findall(r"-?\d+(?:\.\d+)?", reply)
        ok = bool(found) and abs(float(found[0]) - float(expected)) <= tol
        self._mark(ok, marks, str(expected), why)

    def ask_set(self, question, expected, why="", hint=None, marks=1):
        """A set of numbers — order and separators do not matter."""
        reply = self._prompt(question, hint)
        want = sorted(expected)
        shown = ", ".join(str(n) for n in want)
        self._mark(normalise_set(reply) == want, marks, shown, why)

    def ask_re(self, question, pattern, canonical, why="", hint=None, marks=1):
        """Free text matched by regex, for answers with many valid phrasings."""
        reply = self._prompt(question, hint)
        ok = bool(re.search(pattern, normalise(reply)))
        self._mark(ok, marks, canonical, why)

    def ask_sha(self, question, expected_sha, why="", hint=None, marks=1):
        """A flag, checked by hash so it is not sitting in plaintext in lab.py."""
        reply = self._prompt(question, hint)
        ok = sha256(reply.strip()) == expected_sha
        self._mark(ok, marks, "(hash only — go read it off the wire)", why)

    # -- output -------------------------------------------------------------

    def section(self, text: str) -> None:
        print(f"\n{BOLD}{CYAN}== {text}{RESET}")

    def note(self, text: str) -> None:
        print(f"{DIM}{text}{RESET}")

    def finish(self) -> int:
        pct = (self.score * 100 // self.total) if self.total else 0
        print(f"\n{DIM}{RULE}{RESET}")
        print(f"{BOLD}Score: {self.score} / {self.total}  ({pct}%){RESET}")
        if self.missed:
            print(f"{DIM}Missed: {', '.join(str(n) for n in self.missed)}{RESET}")
        if pct >= 90:
            print(f"{OK}Clean run — you read the protocol, not the docs.{RESET}")
        elif pct >= 60:
            print(f"{ACC}Solid. Re-run the ones you missed against the live target.{RESET}")
        else:
            print(f"{ACC}Worth a second pass — the target is still up.{RESET}")
        print()
        return self.score
