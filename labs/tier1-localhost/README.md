# Tier 1 — Your Own Machine

Terminal labs against targets running on `127.0.0.1`. Each lab starts a small
target on your loopback interface, gives you a brief, and marks your answers —
the same self-marking idea as the HTML sheets, moved to the command line where
the real tools live.

Nothing leaves your machine. Nothing is uploaded. Every target is a process you
start and stop yourself.

| Lab | What you do | Marks |
|-----|-------------|-------|
| [01 — HTTP by Hand](./01-http-by-hand/) | Type raw HTTP/1.1 down a netcat socket: status lines, headers, redirects, Basic auth, HEAD, and why a missing `Host` is a 400 | 15 |
| [02 — Port Scanner vs nmap](./02-port-scanner/) | Write a TCP connect scanner, find five hidden services, grab their banners, then race nmap and find out what actually makes it fast | 16 |

---

## Running a lab

Every lab works the same way:

```bash
cd 01-http-by-hand

python3 lab.py start      # bring the target up
python3 lab.py status     # where is it, is it alive
python3 lab.py check      # answer the questions, get marked
python3 lab.py stop       # shut it down
```

On **Windows 11**, use `py` instead of `python3`:

```powershell
py lab.py start
```

Read the lab's own `README.md` first — `check` assumes you have done the work.
At any question, `?` gives a hint and `skip` gives up on that one. Flags are
checked by SHA-256, so reading the lab source will not hand you the answers.

---

## What you need

**Python 3.8 or newer** runs everything here. The lab machinery is standard
library only — no `pip install`, ever.

Beyond that, each lab uses one or two ordinary tools:

| Tool | macOS | Debian / Ubuntu | Windows 11 |
|------|-------|-----------------|------------|
| `python3` | preinstalled (or `brew install python`) | preinstalled | [python.org](https://www.python.org/downloads/) or `winget install Python.Python.3.12` — tick **Add to PATH** |
| `nc` (netcat) | preinstalled | preinstalled | **use `ncat`** — see below |
| `nmap` | `brew install nmap` | `sudo apt install nmap` | [nmap.org/download](https://nmap.org/download) — tick **Add to PATH** |

If a lab is missing something it needs, it tells you which tool and how to
install it before it does anything else.

### Windows 11 notes

The labs themselves are pure Python and run natively in PowerShell or Windows
Terminal — that is why the checkers are `lab.py` and not `check.sh`. Two
practical differences:

- **There is no `nc` on Windows.** The Nmap installer ships **`ncat`**, a
  netcat-compatible rewrite by the Nmap project. Use `ncat` everywhere a brief
  says `nc`; the arguments are identical. You want Nmap for Lab 02 anyway, so
  one install covers both.
- **There is no `printf`.** Where a brief pipes a pre-built request into
  netcat, type the request interactively instead — `ncat 127.0.0.1 8081`, then
  type the lines and finish with a blank one. Or use PowerShell's
  `[Text.Encoding]::UTF8.GetBytes(...)` for the base64 step in Lab 01; the
  brief gives both spellings.

**Or install WSL2** (`wsl --install` in an admin PowerShell, then reboot). That
gives you a real Ubuntu shell with `nc`, `nmap`, `dig`, `tcpdump` and the rest
of the toolkit exactly as the briefs describe them, and it is what most
security courses assume you are typing into. The labs run identically inside
it. Native Windows works fine for these two; WSL2 will matter more as later
labs reach for tools that have no Windows equivalent.

### A note on antivirus

Windows Defender and some third-party AV flag `ncat` and occasionally `nmap` as
"hacktools". They are not malware — they are the standard tools of the trade,
and the flag is a category label, not a detection. Installing from
[nmap.org](https://nmap.org/download) gets you the signed official build.

---

## Scope

`127.0.0.1` only, for both labs. The targets are processes on your own machine.

Port scanning and hand-crafted requests are fingerprintable, and pointing them
at a host you do not own breaks most acceptable-use policies and, in a number
of jurisdictions, the law. Read [../SCOPE.md](../SCOPE.md) before you get
creative. Defining scope before touching anything is itself a Session 3 skill.

---

## Layout

```
tier1-localhost/
├── lib/labkit.py            ← shared: prompting, marking, target processes
├── 01-http-by-hand/
│   ├── README.md            ← the brief — read this first
│   ├── lab.py               ← start / stop / status / check
│   └── server.py            ← the target
└── 02-port-scanner/
    ├── README.md
    ├── lab.py
    ├── listeners.py         ← the target
    ├── scanner-template.py  ← yours to fill in
    └── scanner-reference.py ← peek after you have written your own
```

`.lab-state`, `server.log` and `listeners.log` appear while a target runs and
are gitignored. `.lab-state` holds the current run's answers — do not read it,
and note that stopping the target destroys them.

Unlike the HTML sheets, which are deliberately self-contained one-file
documents, these share `lib/labkit.py`. Shell-level labs are always run from
the repo, so there is no offline-single-file constraint to honour, and one copy
of the marking logic beats four.
