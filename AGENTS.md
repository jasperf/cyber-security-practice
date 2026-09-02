# Cyber Security &amp; CTF Practice — Agent Context

## Project

Interactive self-marking exercise sheets, written independently for personal cyber security exam prep (5 sessions: Cryptography, Networking Fundamentals, Red Teaming, Digital Forensics, Miscellaneous CTF Challenges). Each sheet is a single self-contained HTML file. No build tools, no frameworks, no CDN dependencies beyond Google Fonts. Everything works offline once loaded.

**Live site:** https://jasperf.github.io/cyber-security-practice (auto-deployed from `main` via GitHub Pages, once enabled)

**Stack:** Pure HTML5 + CSS3 + vanilla JavaScript. No build step, no package manager, no server.

## Structure

```
cyber-security-practice/
├── index.html                  ← home page / session index (update when adding sessions)
├── README.md                   ← project overview
├── AGENTS.md                   ← this file
├── SETUP.md                    ← GitHub Pages setup guide
├── LICENSE                     ← MIT license
├── material/                   ← source slide decks (gitignored, kept locally only)
├── s1-cryptography/
├── s2-networking/
├── s3-red-teaming/
├── s4-forensics/
├── s5-misc-ctf/
│   each folder: sessionN-topic.html (interactive) + sessionN-topic.md (printable)
└── labs/                       ← hands-on labs, tiered by setup & risk
    ├── SCOPE.md                ← rules of engagement — read before adding a lab
    ├── crypto-playground/      ← Tier 0: browser-only, same design system as the sheets
    └── tier1-localhost/        ← Tier 1: terminal labs against 127.0.0.1
```

### Labs

The `labs/` tree is a different medium from the session sheets and has its own
conventions:

- **Tier 0** labs are single self-contained HTML files and follow every sheet
  convention above (topbar, tokens, accent colour, flags checked by SHA-256).
- **Tier 1+** labs are terminal labs: a `README.md` brief plus a `lab.py`
  exposing `start` / `stop` / `status` / `check`, sharing `lib/labkit.py`.
  - **Python, not shell** — `check.sh` would need WSL or Git Bash on Windows,
    and these have to run natively on macOS, Linux and Windows 11.
  - **Standard library only.** No `pip install`, matching the repo's no-build-
    tools rule.
  - Targets bind to `127.0.0.1` only, and flags are regenerated on every
    `start` so no answer is ever committed. `check` derives expected values
    from the live target rather than hardcoding them.
  - Runtime files (`.lab-state`, `*.log`) are gitignored.
  - Windows parity is a requirement, not a nice-to-have: no `nc` (use `ncat`),
    no `printf`, use `py` not `python3`. Note both spellings in briefs.
- Every lab brief ends with a **scope note** pointing at `labs/SCOPE.md`.
- **Always update `labs/README.md` and `index.html`** when adding a lab.

## Commands

```bash
# Preview any sheet directly in browser (no server needed)
open s1-cryptography/session1-cryptography.html

# Or serve locally for the index page's links to work
npx serve .                    # install once: npm i -g serve
python3 -m http.server 3000   # Python 3
php -S localhost:3000         # PHP
# Then visit http://localhost:3000

# Git workflow
git add .
git commit -m "Add Session N: Topic exercises"
git push                          # auto-deploys to GitHub Pages
```

## Conventions

- One HTML file per session — fully self-contained with inline CSS and JS
- No external dependencies except Google Fonts (Fraunces, Literata, DM Mono)
- Answers checked client-side; no server, no login, no tracking
- File naming: `sN-topic-slug/sessionN-topic-slug.html` (+ matching `.md`)
- **Always update `index.html`** when adding a new session
- Each session gets its own accent colour (a CSS custom property, `--accent`), so the sessions stay visually distinguishable — pick a colour not already used by another session's card

### Sheet Header Pattern (all sheets must follow this)

Every sheet — regardless of topic — must use the same topbar/header structure:

```html
<canvas id="confetti-canvas"></canvas>

<div class="topbar">
  <div class="topbar-left">
    <div class="logo">Cyber<span>Sec</span> Practice</div>
    <div class="week-badge">Session N &middot; Topic</div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <a href="../index.html" class="back-link">&larr; All sessions</a>
    <div class="timer-wrap"><span style="font-size:0.85rem;">&#9201;</span><div class="timer" id="timer">00:00</div></div>
    <div class="score-pill"><div class="score-label">Score</div><div class="score-val" id="global-score">0 / N</div></div>
  </div>
</div>
<div class="progress-wrap"><div class="progress-bar" id="progress-bar"></div></div>
```

Key rules:
- Logo is always `Cyber<span>Sec</span> Practice` — never a session-specific name
- Topbar uses `<div>`, not `<header>`
- Always include a back-link, timer, and score pill in the right side
- Confetti canvas goes right after `<body>` with `id="confetti-canvas"`
- Sections are anchored (`id="sec-{key}"`) and linked from a `.section-tabs` row under the hero

### Question Card Pattern (all sheets must follow this)

Every question card must have:
1. **Marks badge** in the header: `<span class="q-marks">N mark(s)</span>`
2. **Check/Hint/Reveal buttons** using proper CSS classes (never inline styles):
```html
<div class="q-actions">
  <button class="btn btn-check" onclick="checkMCQ('q1','b')">Check</button>
  <button class="btn btn-hint" onclick="showHint('q1', 'Hint text')">Hint</button>
  <button class="btn btn-reveal" onclick="revealAnswer('q1', 'Answer text')">Show Answer</button>
</div>
<div class="feedback" id="q1-fb"></div>
```
3. **Actions before feedback** — the `q-actions` div must come before the `feedback` div
4. **Every question needs a Check button** — selecting an MCQ option should not auto-check; the student clicks Check when ready
5. **maxMarks must match** the actual sum of the `marks` object's values — verify this when creating sheets
6. Multi-select options use `onclick="selectOpt('q4',this,'a',true)"` (the `true` flag) and `checkMulti('q4',['a','c'])` with a **single-quoted** JS array — the array must never use double quotes, since the array sits inside a double-quoted `onclick="..."` HTML attribute and a `"` there would terminate the attribute early

### Question IDs

- One flat sequence per sheet: `q1`, `q2`, ..., `qN` (no subject-letter prefixes — every sheet in this repo covers one topic, unlike the multi-subject cambridge-practice sheets)
- `marks = { q1: 1, q2: 1, ... }` keyed by question ID
- `sections = { key: { label: '...', qs: ['q1','q2',...] }, ... }` groups question IDs for section-level scoring

### CSS Design Tokens (defined in `:root` on every sheet, and mirrored per-card on `index.html`)
```css
--bg, --surface, --surface2, --border    /* Dark theme layers */
--accent, --accent-rgb                   /* This session's single accent colour */
--text, --text-muted, --text-dim         /* Typography */
--correct, --wrong                       /* Answer feedback */
--font-display, --font-body, --font-mono
--radius                                 /* UI */
```

### Required CSS Classes for Question Actions
Every sheet must define these button classes (never use inline styles on buttons):
- `.btn` — base button styling (mono font, padding, border-radius, transition)
- `.btn-check` — primary action button (session accent colour)
- `.btn-hint` — subtle hint button (surface background, muted text)
- `.btn-reveal` — minimal show-answer button (transparent, dim text)
- `.q-actions` — flex container for the button row
- `.q-marks` — marks badge in question header

### JavaScript State Pattern
- Central `state` object: `{ answers, correct, startTime }`
- `marks`, `sections`, `allQs`, `maxMarks` computed once at the top of `<script>`
- All UI derives from state; DOM is just a representation
- Persistence via `localStorage` with a session-slug + timestamp key

### Common Functions
- `selectOpt(qid, el, val, isMulti)` — track single or multi selection
- `checkMCQ(qid, correctVal)` — single choice
- `checkMulti(qid, correctValsArray)` — multi-select (array must use single quotes, see above)
- `checkNum(qid, correctVal, tolerance)` — numeric with optional tolerance
- `showHint(qid, hintText)`, `revealAnswer(qid, answerText)`
- `markResult(qid, isCorrect)` — update UI and state
- `updateScores()` — recalculate and update score displays
- `showResults(total)` — display final panel with confetti
- `launchConfetti()` — canvas-based animation

## Constraints

- Do not introduce build tools, bundlers, or npm packages.
- Keep each session sheet fully self-contained — no shared JS files.
- Do not add frameworks (React, Vue, etc.).
- Always update `index.html` when adding a new session.
- Do not mention the AI tool used to assist with this project by name.
- `.DS_Store` and the `material/` folder are gitignored (source slide decks stay local, not committed).

## Git

- Atomic commits: one logical change per commit (e.g. one new session, one bug fix, one index update — not all at once).
- GitHub Pages auto-deploys from `main` within ~30 seconds of push.
