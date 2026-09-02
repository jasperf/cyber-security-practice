# Hands-On Labs

The quiz sheets in this repo test *recall*. These labs make you *do* the thing —
hash it, break it, encrypt it, capture the flag. Same self-marking philosophy,
different medium.

Labs are organised in four tiers by how much setup (and risk) they need. Only
**Tier 0** is built so far; the rest is a roadmap for future sessions.

---

## Tier 0 — Browser only (no setup) ✅

Runs entirely client-side, publishes straight to the live GitHub Pages site,
needs no terminal, no server, no accounts. Nothing you type leaves your browser.

| Lab | What you do | Status |
|-----|-------------|--------|
| [Crypto Playground](./crypto-playground/crypto-playground.html) | Live hashing + avalanche effect · encoding chains (Base64/hex/ROT13/XOR) · Caesar breaker (χ² frequency analysis) · AES-GCM encrypt/decrypt with PBKDF2 · **Ed25519 signing** (the maths behind your SSH keys, with real `SHA256:` fingerprints) · the **ECB penguin** leaking through ciphertext · 6 hash-verified CTF flags | ✅ Live |

The Crypto Playground is the Session 1 companion: every tool maps to a quiz
question (ECB → Q10, GCM/authentication → Q11–Q12, frequency analysis → Q6–Q7).
The flags are checked by SHA-256 comparison, so the answers are not in view-source.

**Built with the same design system as the session sheets** — same CSS tokens,
topbar, accent-per-page convention. The AES for the ECB demo is hand-rolled
(WebCrypto deliberately won't expose ECB) and verified against the FIPS-197 test
vectors; MD5 is verified against RFC 1321.

### Tier 0 ideas not yet built
- **Networking playground** (Session 2 companion): subnet/CIDR calculator, an
  OSI-layer packet-dissection drill, a "which port is this?" trainer.
- **Forensics playground** (Session 4 companion): magic-byte file-type identifier,
  EXIF/metadata reader, a stego "spot the hidden bits" LSB viewer — all on files
  the user drops in locally (never uploaded).

---

## Tier 1 — Your machine & your LAN (roadmap)

Uses tools already installed locally (`nmap`, `openssl`, `dig`, `whois`, `nc`,
`tcpdump`, `python3`, `gpg`). Each lab is a markdown brief plus a `check.sh` that
marks a verifiable answer ("how many hosts responded?", "what TTL?").

Planned: map your own subnet and identify devices by MAC OUI · capture a DNS
query with tcpdump and decode it by hand · write a Python TCP port scanner and
race it against nmap · hand-craft an HTTP request over `nc`.

**Scope:** `127.0.0.1` and your own LAN only. See [SCOPE.md](./SCOPE.md) before running anything.

---

## Tier 2 — imagewize.com, read-only (roadmap)

Audit a box you own — but it's *production*, so audit, don't attack.
TLS/cipher inspection with `openssl s_client` · security-header grading ·
SPF/DKIM/DMARC/CAA record review with `dig` · SSH config review · reading real
fail2ban/auth logs to see live bot traffic. The `wp-ops` tooling
(`security_scan`, `server_status`, `ip_reputation_check`) fits here.

**Scope:** `imagewize.com` (owned by the repo author). Nothing intrusive — no
scanning, fuzzing, or exploitation against the live host.

---

## Tier 3 — Docker targets (roadmap)

The only ethically clean place for anything *offensive*: deliberately-vulnerable
containers you spin up and throw away. DVWA, OWASP Juice Shop, an outdated
WordPress. SQLi, XSS, and cracking hashes *you* generated with john/hashcat.
This is the one tier that adds Docker to the workflow; it lives entirely under
`labs/` and never touches the session sheets.

**Scope:** local Docker containers only.

---

## Rules of engagement

Writing down scope *is* part of the curriculum (Session 3, red teaming). The
short version, in [SCOPE.md](./SCOPE.md): the only legal targets are your own
loopback, your own LAN, `imagewize.com`, and disposable local containers.
Scanning is fingerprintable and most hosting AUPs forbid outbound scans — never
point any of these tools at a host you don't own.
