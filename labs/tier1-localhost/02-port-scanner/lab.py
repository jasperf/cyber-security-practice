#!/usr/bin/env python3
"""Lab 02 — Write a port scanner, then race nmap. Target control and checker.

    python3 lab.py start     # open some services on random loopback ports
    python3 lab.py status    # is the target up?
    python3 lab.py check     # answer the questions, get marked
    python3 lab.py stop      # shut it down

On Windows 11 use `py lab.py start` (or `python lab.py start`).
"""

from __future__ import annotations

import os
import random
import secrets
import sys

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(LAB_DIR), "lib"))

import labkit as kit  # noqa: E402

RANGE_LO, RANGE_HI = 9000, 9100
SERVICE_COUNT = 5
LOG_PATH = os.path.join(LAB_DIR, "listeners.log")
STATE = kit.State(LAB_DIR)


# ------------------------------------------------------------------ start ----

def pick_ports() -> list[int]:
    """Random free ports inside the advertised range — reshuffled every start."""
    candidates = list(range(RANGE_LO, RANGE_HI + 1))
    random.shuffle(candidates)
    chosen = []
    for port in candidates:
        if not kit.port_open(port):
            chosen.append(port)
        if len(chosen) == SERVICE_COUNT:
            return sorted(chosen)
    raise SystemExit("could not find %d free ports in %d-%d" % (SERVICE_COUNT, RANGE_LO, RANGE_HI))


def cmd_start() -> int:
    if os.path.exists(STATE.path):
        old = STATE.load()
        if any(kit.port_open(p) for p in old["ports"]):
            print(f"\nTarget already up. Stop it first to reshuffle the ports.\n")
            return 0
        STATE.clear()

    # Whatever range we pick, the student's own machine may already be
    # listening somewhere inside it — so record what was open before we start.
    preexisting = kit.scan_range(RANGE_LO, RANGE_HI)

    ports = pick_ports()
    flag_port = random.choice(ports)
    flag = "CTF{scan_%s}" % secrets.token_hex(6)

    pid = kit.spawn(
        [
            sys.executable,
            os.path.join(LAB_DIR, "listeners.py"),
            "--ports", ",".join(str(p) for p in ports),
            "--flag", flag,
            "--flag-port", str(flag_port),
        ],
        LOG_PATH,
    )

    if not all(kit.wait_for_port(p) for p in ports):
        kit.kill(pid)
        print(f"\n{kit.BAD}Target failed to start.{kit.RESET} See {LOG_PATH}\n")
        return 1

    STATE.save(
        pid=pid,
        ports=ports,
        flag_port=flag_port,
        flag_sha=kit.sha256(flag),
        range_lo=RANGE_LO,
        range_hi=RANGE_HI,
        preexisting=preexisting,
    )

    neighbours = ""
    if preexisting:
        neighbours = (
            f"\n  {kit.ACC}Note:{kit.RESET} {len(preexisting)} port(s) in this range were "
            f"already open\n  before the lab started — services of your own. Your scan will "
            f"find\n  them too, and the checker expects them. That is realistic: on a real\n"
            f"  host you never get a clean range.\n"
        )

    print(f"""
{kit.BOLD}{kit.ACC}Target up{kit.RESET} — {SERVICE_COUNT} services somewhere in
{kit.BOLD}127.0.0.1:{RANGE_LO}-{RANGE_HI}{kit.RESET}  (pid {pid})

  Which ports, is the point of the lab. {kit.DIM}(And no, do not read
  .lab-state — it holds the answer and marking yourself is the whole idea.){kit.RESET}
{neighbours}
  Connection log: {LOG_PATH}
     Watch it while you scan; you are looking at what your own traffic
     looks like from the defender's side.

  Work through README.md, then: {kit.BOLD}{kit.python_cmd()} lab.py check{kit.RESET}
""")
    kit.advise("nmap", ("nc", "ncat"))
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
    print("\nListeners stopped. That port set and flag are gone.\n")
    return 0


def cmd_status() -> int:
    if not os.path.exists(STATE.path):
        print(f"\nTarget is {kit.BOLD}down{kit.RESET}. Start it: "
              f"{kit.BOLD}{kit.python_cmd()} lab.py start{kit.RESET}\n")
        return 1
    state = STATE.load()
    live = sum(1 for p in state["ports"] if kit.port_open(p))
    print(f"\n{live} of {len(state['ports'])} listeners responding "
          f"in {state['range_lo']}-{state['range_hi']} (pid {state['pid']})\n")
    return 0 if live else 1


# ------------------------------------------------------------------ check ----

def cmd_check() -> int:
    state = STATE.load()
    ports = state["ports"]
    if not any(kit.port_open(p) for p in ports):
        print(f"\n{kit.BAD}No listener is answering.{kit.RESET} "
              f"Run {kit.BOLD}{kit.python_cmd()} lab.py start{kit.RESET} again.\n")
        return 1

    # The truth is whatever is actually listening right now, not just our own
    # listeners — the student's machine may have services in the range too.
    live = kit.scan_range(state["range_lo"], state["range_hi"])
    foreign = [p for p in live if p not in ports]

    lab = kit.Lab(
        "Lab 02 — Write a port scanner, then race nmap",
        f"Answer from your own scan of 127.0.0.1:{state['range_lo']}-{state['range_hi']}.",
    )

    lab.section("What your scanner found")

    lab.ask_set(
        f"Which ports in {state['range_lo']}-{state['range_hi']} are open? "
        "(any order, any separator)",
        live,
        "A connect scan is nothing more than this: try to complete a TCP "
        "handshake on every port and write down which ones let you."
        + (
            f"  {len(foreign)} of those ({', '.join(str(p) for p in foreign)}) "
            "are not this lab's — they are your own machine's services, and "
            "noticing that they are there is part of the exercise."
            if foreign else ""
        ),
        hint="Your scanner and nmap should agree exactly. If they do not, your "
             "timeout is too short — or you assumed only the lab is listening.",
        marks=2,
    )

    lab.ask_num(
        "How many ports were open?",
        len(live),
        why="On a real host this number is the attack surface. Every open port "
            "is software listening to the network, and software has bugs.",
    )

    lab.section("Banner grabbing")

    lab.ask_num(
        "Connect to each open port and read the line it sends. Which port hands "
        "out the flag?",
        state["flag_port"],
        why="Services announce themselves unprompted. `nc <host> <port>` and "
            "waiting one second is the entire technique.",
        hint="nc 127.0.0.1 <port> — it talks first, you do not have to send "
             "anything.",
    )

    lab.ask_sha(
        "What is the flag?",
        state["flag_sha"],
        "Those other banners carry version numbers — `lab-ftp 1.2.3`, "
        "`LabSSH_1.0`. On a real target that string goes straight into a CVE "
        "search, which is why version-hiding is standard hardening.",
        marks=2,
    )

    lab.section("How nmap does it")

    lab.ask_re(
        "Which nmap flag runs a TCP connect scan — the same technique your "
        "Python scanner used?",
        r"-\s*st\b|connect",
        "-sT (TCP connect scan)",
        "It completes the full three-way handshake using the OS socket API, "
        "exactly like your scanner. It is also the default when you are not "
        "root, because it needs no special privileges.",
        hint="Two letters after the dash. It is the unprivileged default.",
    )

    lab.ask_re(
        "Which nmap scan type is the default *when running as root*, and needs "
        "those privileges?",
        r"-\s*ss\b|syn|half.?open|stealth",
        "-sS (SYN / half-open scan)",
        "It sends SYN, reads the reply, and never completes the handshake.",
        hint="It is the 'half-open' one.",
    )

    lab.ask_re(
        "Why does that scan need root/administrator privileges?",
        r"raw (socket|packet)|craft.*packet|packet.*craft|kernel bypass|"
        r"below the (os|kernel|socket)",
        "it builds raw packets itself, and raw sockets are privileged",
        "Normal sockets make the kernel do the handshake for you. To send a SYN "
        "and then walk away you have to write the TCP header yourself — a raw "
        "socket — and every OS gates that behind admin rights.",
        hint="What does it have to build by hand that a normal socket builds for you?",
    )

    lab.section("Reading the results")

    lab.ask_re(
        "When you try to connect to a *closed* TCP port, what does the host send "
        "back?",
        r"\brst\b|reset",
        "a RST (reset) packet",
        "Closed means 'nothing is listening, and I am telling you so'. That "
        "answer is itself information: the host is alive.",
        hint="A three-letter TCP flag.",
    )

    lab.ask_re(
        "nmap labels some ports `filtered` rather than open or closed. What does "
        "that mean?",
        r"no (response|reply|answer)|nothing (came )?back|drop|firewall|"
        r"silently|timed? ?out",
        "no reply at all — something dropped the probe (usually a firewall)",
        "Open and closed are both *answers*. Filtered is silence, which usually "
        "means a firewall swallowed the packet rather than rejecting it — and "
        "silence is why scans are slow: you can only wait out the timeout.",
        hint="It is about what did *not* happen.",
    )

    lab.ask_re(
        "Scanning loopback, your sequential and parallel scans took roughly the "
        "same time. Why does parallelism buy you almost nothing here?",
        r"rst|reset|instant|immediat|no (wait|delay|latency|timeout)|"
        r"never (wait|time)|nothing to wait|no round.?trip|fast",
        "nothing ever waits — closed loopback ports RST instantly, so there is "
        "no timeout to overlap",
        "Parallelism hides *waiting*. On loopback there is no waiting: every "
        "port answers in microseconds, open or closed. Concurrency only pays "
        "for itself when probes sit idle.",
        hint="What would you have to be waiting for, for running probes at once "
             "to help?",
    )

    lab.ask_re(
        "Re-run it with `--probe-delay 0.05` to fake network latency. Now the "
        "parallel scan is dramatically faster. What is it doing that the loop "
        "is not?",
        r"parallel|concurren|at once|simultaneous|thread|async|batch|"
        r"in flight|overlap|multiple .* time",
        "keeping many probes in flight at once instead of one at a time",
        "That is nmap's real advantage on a live network: hundreds of "
        "outstanding probes, with the rate tuned as it learns the target — "
        "which is what -T0..-T5 sets. The slowest thing in any scan is a "
        "filtered port you have to wait out.",
        hint="Think about what your loop is doing during each 50ms delay.",
    )

    lab.section("Flags worth knowing")

    lab.ask(
        "Which nmap flag asks for service and version detection — the automated "
        "version of the banner grabbing you did by hand?",
        "-sV",
        "It goes further than reading the banner: it sends protocol-specific "
        "probes and matches the replies against a fingerprint database.",
        hint="Capital letter after -s.",
    )

    lab.ask_num(
        "With no -p option at all, how many ports does nmap scan by default?",
        1000,
        why="The 1000 most common, not the first 1000 — ranked by how often each "
            "was found open in real internet-wide scans. It is a shortcut, and "
            "it will miss a service parked on a high port exactly like this "
            "lab's.",
        hint="A round number, and it is not 65535.",
    )

    lab.ask_re(
        "What does `nmap -p- 127.0.0.1` scan?",
        r"all|every|65535|65,535|1-65535|whole range|full range",
        "all 65535 TCP ports",
        "The complete TCP port space. Slow, thorough, and the thing to run when "
        "a default scan finds suspiciously little.",
    )

    lab.finish()
    print(f"{kit.DIM}Listeners still running. "
          f"Stop them with: {kit.python_cmd()} lab.py stop{kit.RESET}\n")
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
