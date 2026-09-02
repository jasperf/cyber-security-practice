# Cyber Security &amp; CTF Practice

Interactive self-marking exercise sheets I wrote for my own cyber security exam prep — cryptography, networking fundamentals, red teaming, digital forensics, and miscellaneous CTF challenges.

## Live Site

👉 **[jasperf.github.io/cyber-security-practice](https://jasperf.github.io/cyber-security-practice)** (once GitHub Pages is enabled — see [SETUP.md](./SETUP.md))

## What's Inside

Each session sheet is a single self-contained HTML file with:
- Multiple choice and multi-select questions
- Instant answer checking with correct/wrong feedback
- Hints and worked answer reveals
- Live score tracker and session timer
- No dependencies, no server required — pure HTML/CSS/JS

## Structure

```
cyber-security-practice/
├── index.html                        ← Home page / session index
├── s1-cryptography/
│   ├── session1-cryptography.html    ← Interactive (21 q · 24 marks)
│   └── session1-cryptography.md      ← Printable, same questions
├── s2-networking/
│   ├── session2-networking.html      ← Interactive (21 q · 22 marks)
│   └── session2-networking.md        ← Printable
├── s3-red-teaming/
│   ├── session3-red-teaming.html     ← Interactive (20 q · 21 marks)
│   └── session3-red-teaming.md       ← Printable
├── s4-forensics/
│   ├── session4-forensics.html       ← Interactive (19 q · 21 marks)
│   └── session4-forensics.md         ← Printable
├── s5-misc-ctf/
│   ├── session5-misc-ctf.html        ← Interactive (20 q · 21 marks)
│   └── session5-misc-ctf.md          ← Printable
├── material/                         ← Source slide decks (gitignored, kept locally)
└── README.md
```

## Printable Worksheets (Parallel Path)

Alongside each interactive HTML sheet, a **printable markdown worksheet** is available for offline/classroom use — same basename, `.md` instead of `.html`, in the same session folder. They contain the exact same questions, formatted for printing or copying into a notebook.

Use the printable versions for **written practice** and the interactive versions for **self-assessment with hints and instant feedback**.

## Adding a New Sheet

1. Create a new folder (e.g. `s6-web-exploitation/`) with `sessionN-topic.html` and `sessionN-topic.md`.
2. Copy an existing sheet as your starting template — the design system (CSS tokens, question-card markup, JS check functions) is the same across every sheet, only the accent colour and content change per session.
3. Update questions, options, correct answers, hints, and marks.
4. Update `index.html` to add a card for the new session.
5. Push to `main` — GitHub Pages publishes automatically.

## Local Development

```bash
# Clone the repo
git clone https://github.com/jasperf/cyber-security-practice.git
cd cyber-security-practice

# Open any file directly in your browser — no build step needed
open s1-cryptography/session1-cryptography.html

# Or run a simple local server (optional, for index page links)
npx serve .
# then visit http://localhost:3000
```

## Generating PDFs

The printable `.md` worksheets can be turned into a PDF locally with [pandoc](https://pandoc.org/) — no PDFs are committed to the repo (see `.gitignore`), so generate one whenever you need it:

```bash
pandoc -f gfm s1-cryptography/session1-cryptography.md -o session1-cryptography.pdf \
  --pdf-engine=xelatex -V geometry:margin=2.2cm -V fontsize=11pt -V colorlinks=true
```

`-f gfm` matters: these sheets write MCQ options as a `-` list directly under the question line with no blank line before it (as GitHub renders it). Pandoc's default markdown reader needs that blank line to start a list, so without `-f gfm` the options collapse into run-on paragraph text instead of bullets. Requires `pandoc` and a LaTeX engine (`xelatex`, from a TeX distribution like MacTeX/TeX Live) installed locally.

## Sessions Covered

| Session | Topic | Status |
|---------|-------|--------|
| 1 | Cryptography — cryptology basics, classical &amp; modern ciphers, AES modes, real-world pitfalls, side channels | ✅ Live |
| 2 | Networking Fundamentals — OSI model, TCP/IP, IP addressing, TCP/UDP, ports &amp; scanning | ✅ Live |
| 3 | Red Teaming — Red vs Blue, Unix fundamentals, C &amp; Python for CTF, cracking &amp; scanning tools | ✅ Live |
| 4 | Digital Forensics — 6-stage process, evidence types, encodings &amp; steganography, emerging challenges | ✅ Live |
| 5 | Miscellaneous CTF Challenges — challenge categories, social engineering, OSINT, hardware CTFs, mindset | ✅ Live |

## Tech

Pure HTML + CSS + JavaScript. No frameworks, no build tools, no CDN dependencies beyond Google Fonts. Every file works offline once loaded.

---

*Independent personal study notes for exam preparation, testing general cyber security concepts in my own words. Not a reproduction of any course's materials, and not affiliated with or endorsed by any course, instructor, or organization.*
