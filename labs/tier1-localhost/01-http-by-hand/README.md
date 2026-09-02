# Lab 01 — HTTP by Hand

**Tier 1 · target: `127.0.0.1` · ~30 minutes · 15 marks**

You have used HTTP every day for years without ever seeing one. In this lab you
type the requests yourself, byte for byte, over a raw TCP socket — no browser,
no `curl`, no library. By the end you will have done a full authenticated
transaction with nothing but a keyboard.

This matters beyond curiosity. Every web attack is a request the server did not
expect, and you cannot craft one you cannot spell.

---

## Start the target

```bash
python3 lab.py start        # macOS / Linux
py lab.py start             # Windows 11
```

It binds a small HTTP/1.1 server to `127.0.0.1` — your own machine, nothing
else. It prints the port and the credentials you will need later. Every start
regenerates the flags, so the answers are never the same twice and are never
stored in this repo.

Useful while you work:

```bash
python3 lab.py status       # port, pid, credentials
python3 lab.py stop         # shut it down when you are done
```

Watch your own requests land, in a second terminal:

```bash
tail -f server.log                       # macOS / Linux
Get-Content server.log -Wait             # Windows PowerShell
```

---

## Speaking HTTP with netcat

`nc` opens a raw TCP connection and gets out of the way — whatever you type
goes down the wire untouched.

```bash
nc 127.0.0.1 <port>
```

Then type a request and **end it with a blank line**. The blank line is not
cosmetic: it is how the server knows the header block is over.

```http
GET / HTTP/1.1
Host: 127.0.0.1
Connection: close

```

`Connection: close` tells the server to hang up after replying. Leave it out and
HTTP/1.1 keep-alive holds the socket open, and `nc` will just sit there looking
frozen. That is not a bug — it is the feature that lets a browser fetch fifty
images down one connection.

Prefer to fire a whole request in one shot?

```bash
printf 'GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n' \
  | nc 127.0.0.1 <port>
```

> **Windows 11:** Windows has no `nc`. Install [Nmap](https://nmap.org/download)
> — it ships **`ncat`**, a netcat-compatible rewrite by the Nmap project. Use
> `ncat` everywhere this brief says `nc`; the arguments are the same. You will
> want Nmap for Lab 02 anyway. There is no `printf` in PowerShell either, so
> type requests interactively, or use WSL if you would rather have the whole
> Unix toolkit.

---

## What to find out

Work through these against the running target. The checker will ask for each.

**The response line and headers**

1. Send `GET / HTTP/1.1`. Write down the exact **status line** that comes back.
2. Find the **`Server:`** header. Note its value.
3. Request `/flag.txt` and note its **`Content-Length`**, in bytes.

**Reading a body**

4. Read the **flag** out of `/flag.txt`. Notice where the body begins: after the
   blank line, and not one byte earlier.

**Status codes that are not 200**

5. Request something that does not exist — `/nope.txt`. What code?
6. Request `/old-page`. What code, and **which header** tells you where it went?
   Follow it by hand.

**Authentication**

7. Request `/secret` with no credentials. What code comes back, and what
   **realm** does the `WWW-Authenticate` header name?
8. Now authenticate. HTTP Basic wants `user:password` base64-encoded:

   ```bash
   printf 'labuser:PASSWORD' | base64                       # macOS / Linux
   ```
   ```powershell
   [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('labuser:PASSWORD'))
   ```

   Then send it as a header and read the second flag:

   ```http
   GET /secret HTTP/1.1
   Host: 127.0.0.1
   Authorization: Basic <your base64 string>
   Connection: close

   ```

   Look hard at what you just did. That string is *encoded*, not encrypted —
   anyone watching the wire reverses it in a second. This is why HTTP Basic
   outside TLS is indefensible.

**The rules of the protocol**

9. Send `HEAD /` instead of `GET /`. Compare the two responses line by line.
   What is different, and what is identical?
10. Send an HTTP/1.1 request with **no `Host:` header**. What happens, and why
    would a server care?

---

## Mark yourself

```bash
python3 lab.py check
```

Type `?` at any question for a hint, or `skip` to give up on one. Flags are
checked by SHA-256 comparison, so reading `lab.py` will not hand you the
answers — the same trick the Crypto Playground uses.

Then clean up:

```bash
python3 lab.py stop
```

---

## Where this shows up

- **Session 2 (Networking)** — the application layer of the OSI model, in the
  flesh: you are hand-writing layer 7 on top of a layer 4 socket.
- **Session 3 (Red Teaming)** — banner grabbing and header enumeration are the
  first minutes of any web engagement. The `Server:` header alone often names
  the software *and* version to look up.
- **Session 5 (CTF)** — web challenges routinely need a request a browser will
  not send: a forged header, an odd method, a deliberately malformed line.

## Scope

`127.0.0.1` only. The target is a process on your own machine, started and
stopped by you. See [../../SCOPE.md](../../SCOPE.md) — never point these
techniques at a host you do not own.
