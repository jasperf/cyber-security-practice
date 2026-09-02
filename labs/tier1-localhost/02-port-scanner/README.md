# Lab 02 — Write a Port Scanner, Then Race nmap

**Tier 1 · target: `127.0.0.1` · ~45 minutes · 16 marks**

nmap feels like magic until you write the twenty lines it is built on. In this
lab you write a TCP connect scanner yourself, find five services hiding on
random loopback ports, grab their banners, and then run nmap over the same
range to see what a real scanner adds.

The lesson at the end is not "nmap is faster". It is *why* it is faster, and
the honest answer turns out to be more interesting than you would expect.

---

## Start the target

```bash
python3 lab.py start        # macOS / Linux
py lab.py start             # Windows 11
```

Five fake services bind to random ports somewhere in **9000–9100** on
`127.0.0.1`. Which ports is the point of the lab, so they are not printed.
Every start reshuffles them.

If some of that range is already in use by your own machine, `start` says so.
Your scan will find those too, and the checker expects them — on a real host
you never get a clean range.

```bash
python3 lab.py status       # how many listeners are answering
python3 lab.py stop         # shut them down
```

Watch the connections arrive, in a second terminal:

```bash
tail -f listeners.log                    # macOS / Linux
Get-Content listeners.log -Wait          # Windows PowerShell
```

Leave that running while you scan. What you see is what a scan looks like from
the defender's side — and it is why scanning hosts you do not own is both
rude and trivially detectable.

---

## Part 1 — Write the scanner

Open [`scanner-template.py`](./scanner-template.py). It has five TODOs and the
whole thing lands in about twenty lines.

```bash
python3 scanner-template.py 9000 9100
```

The idea in one sentence: **try to complete a TCP handshake with every port in
the range, and write down which ones let you.** That is a connect scan. There
is nothing else to it.

Three things worth getting right:

- **`connect_ex()`, not `connect()`** — it returns `0` on success and an error
  number otherwise, instead of raising. Much easier to loop over.
- **Set a timeout.** Without one, a port that never answers will hang you for
  a minute or more. `sock.settimeout(0.3)` is plenty on loopback.
- **Close your sockets.** A `with` block does it. Run out of file descriptors
  and the scan starts reporting closed ports that are actually open.

When it works, note **which ports are open** and **how many**.

## Part 2 — Grab the banners

Connect to each open port and *say nothing*. Most services introduce
themselves first:

```bash
nc 127.0.0.1 <port>          # macOS / Linux  (ncat on Windows)
```

One of them hands you the flag. The others give you version strings —
`lab-ftp 1.2.3`, `SSH-2.0-LabSSH_1.0`. On a real target that string goes
straight into a CVE search, which is exactly why "hide your version banners"
is on every hardening checklist.

## Part 3 — Race nmap

```bash
nmap -p 9000-9100 127.0.0.1
nmap -p 9000-9100 -sV 127.0.0.1      # service/version detection
```

Your list and nmap's should match exactly. If they do not, your timeout is too
short — or you assumed only the lab was listening.

Then make your scanner concurrent (`ThreadPoolExecutor`, ~100 workers) and time
both versions. [`scanner-reference.py`](./scanner-reference.py) does this for
you if you would rather compare after writing your own:

```bash
python3 scanner-reference.py 9000 9100 --banners
```

**You will find they take the same time.** That is not a bug in your code. On
loopback a closed port answers with a RST in microseconds — there is no waiting
for concurrency to hide. Parallelism speeds up *waiting*, and here nothing
waits.

To see the effect that makes nmap fast on a real network, fake the latency:

```bash
python3 scanner-reference.py 9000 9100 --probe-delay 0.05
```

Now the sequential scan crawls and the parallel one does not. That gap — one
probe at a time versus hundreds in flight — is nmap's actual advantage, and it
only exists because real networks make you wait.

---

## Things to know before you check

The questions cover what you found, plus the concepts behind it:

- **`-sT` vs `-sS`** — which one your Python scanner is, which one needs root,
  and why. (Think about what a half-open scan has to build by hand that the
  kernel builds for you.)
- **open / closed / filtered** — what the host sends back in each case, and
  which of the three is silence.
- **`-sV`**, **`-p-`**, and how many ports nmap scans when you give it no `-p`
  at all.

---

## Mark yourself

```bash
python3 lab.py check
```

`?` for a hint, `skip` to give up on a question. The flag is checked by
SHA-256, so reading `lab.py` will not hand it to you.

```bash
python3 lab.py stop
```

---

## Where this shows up

- **Session 2 (Networking)** — the TCP three-way handshake, and ports as the
  transport layer's addressing scheme. You are now using both by hand.
- **Session 3 (Red Teaming)** — enumeration is the first phase of every
  engagement, and a port scan is its first move. Knowing that a SYN scan is
  "stealthier" only means something once you know it never completes the
  handshake, so older loggers never recorded it.
- **Session 4 (Forensics)** — `listeners.log` is the other half of this: what
  the scan looked like to the target. Detection is pattern-matching on exactly
  that.

## Scope

`127.0.0.1` only. **Do not point a scanner at anything you do not own.** Port
scans are trivially fingerprintable, most ISP and hosting acceptable-use
policies forbid them outright, and in several jurisdictions an unauthorised
scan is itself an offence. See [../../SCOPE.md](../../SCOPE.md).
