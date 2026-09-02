# Rules of Engagement — Lab Scope

Defining scope before touching anything is itself a red-teaming skill
(Session 3). These labs stay strictly inside targets the author owns or that are
disposable. **Never point any tool in these labs at a host you do not own or
have written permission to test.**

## In scope

| Target | Allowed | Notes |
|--------|---------|-------|
| `127.0.0.1` / `localhost` | Anything | Your own machine. |
| Your own LAN (e.g. `192.168.0.0/16`, `10.0.0.0/8`) | Discovery & inspection | Devices you own on your own network. |
| `imagewize.com` | **Read-only audit only** | Owned by the author, but it's a *production* host. TLS inspection, header/DNS review, reading your own logs. No scanning, fuzzing, exploitation, or load. |
| Local Docker containers (DVWA, Juice Shop, etc.) | Anything, incl. offensive | Disposable, isolated, deliberately vulnerable. The only place to practise attacks. |

## Out of scope — never

- Any host, IP, or domain not listed above.
- Scanning, brute-forcing, or exploiting `imagewize.com` or any shared hosting.
- Anything that degrades a production service (DoS, heavy fuzzing, credential spraying).
- Third-party sites, "just to test" — port scanning is fingerprintable and most
  hosting/ISP acceptable-use policies forbid outbound scans.

## Why this matters

Unauthorised scanning or access can breach your VPS provider's AUP, your ISP's
terms, and in many jurisdictions the law. Owning the box is what makes Tier 2
legitimate — and keeping it read-only is what keeps it responsible. Offensive
practice belongs on the disposable Docker targets in Tier 3, nowhere else.
