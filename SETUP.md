# Setting Up cyber-security-practice on GitHub Pages

The local folder, git repo, and all commits already exist on your computer at `~/code/cyber-security-practice`. This guide covers the two steps that need your GitHub login: creating the remote repo, and enabling Pages.

---

## Step 1 — Create the repo on GitHub

1. Go to **github.com/new** (make sure you're logged in as `jasperf`)
2. Fill in:
   - **Repository name:** `cyber-security-practice`
   - **Description:** `Interactive self-marking exercise sheets for cyber security & CTF practice`
   - **Visibility:** Public *(required for free GitHub Pages)*
   - Leave "Initialize with README" **unchecked** — the repo already has one
3. Click **Create repository**
4. Keep the page open — you'll need the remote URL in Step 2

---

## Step 2 — Connect and push

```bash
cd ~/code/cyber-security-practice

# Connect to GitHub (paste the URL from Step 1)
git remote add origin https://github.com/jasperf/cyber-security-practice.git

# Push
git branch -M main
git push -u origin main
```

If prompted for credentials, use your GitHub username and a **Personal Access Token**
(not your password). Generate one at: github.com/settings/tokens → New classic token → scope: `repo`.

---

## Step 3 — Enable GitHub Pages

1. Go to your repo: **github.com/jasperf/cyber-security-practice**
2. Click **Settings** (top tab)
3. Scroll to **Pages** in the left sidebar
4. Under **Source**, set:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**
6. Wait ~60 seconds, then visit:

   👉 **https://jasperf.github.io/cyber-security-practice**

---

## Step 4 — Adding new sessions (weekly workflow)

```bash
cd ~/code/cyber-security-practice

# Create the next session's folder (copy an existing one as a template)
cp -r s5-misc-ctf s6-web-exploitation
cd s6-web-exploitation
mv session5-misc-ctf.html session6-web-exploitation.html
mv session5-misc-ctf.md session6-web-exploitation.md

# Edit the new files in VS Code
code session6-web-exploitation.html

# Add a card for it in index.html, then push it live:
cd ~/code/cyber-security-practice
git add .
git commit -m "Add Session 6: Web Exploitation exercises"
git push
```

GitHub Pages auto-deploys within ~30 seconds of every push. No build step needed.

---

## Optional: Custom domain

If you buy a domain (e.g. `cybersecpractice.dev`), create a `CNAME` file in the repo root with the domain name, commit and push it, then point your registrar's DNS `CNAME` record for `www` at `jasperf.github.io`. Enable **Enforce HTTPS** in GitHub Settings → Pages once it propagates (10–30 minutes).

---

## Quick reference commands

| Task | Command |
|------|---------|
| Check status | `git status` |
| See what changed | `git diff` |
| Stage all changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push live | `git push` |
| Pull latest | `git pull` |
| Open in VS Code | `code .` |
