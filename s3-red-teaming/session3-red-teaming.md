# Session 3 · Red Teaming

**Personal Study Notes · Printable Worksheet**
**20 questions · 21 marks**

This document contains all questions from the interactive sheet in a printable format. Write your answers directly in your notebook, then self-check afterwards using the interactive `.html` version.

---

## Section A: Red Team Fundamentals

**Key ideas:** **Red teams** act as the adversary, using real attack techniques to probe an organisation's defences. **Blue teams** defend and respond. A **CTF** (Capture The Flag) challenges participants to use red-teaming technique to find a hidden text string, the "flag".

### Questions

**Q1** (1 mark)
In cybersecurity, the Red Team's role is best described as:
- A) Defending the network from attacks
- B) Acting as the adversary, using real attack techniques to find weaknesses
- C) Writing security policy documents
- D) Only performing paperwork audits

**Q2** (2 marks)
What is the correct order of the standard red-teaming attack chain given in the lecture?
- A) Privilege escalation → Initial access → C2 → Objective
- B) Initial access → Vulnerability exploitation → Attack road map design → Privilege escalation → Command & control → Objective
- C) Objective → Initial access → Command & control
- D) Command & control → Privilege escalation → Initial access

**Q3** (1 mark)
What does CTF stand for in a cybersecurity competition context?
- A) Cyber Threat Forensics
- B) Capture The Flag
- C) Critical Test Framework
- D) Controlled Traffic Filtering

---

## Section B: Unix Fundamentals

**Key ideas:** Unix/Linux is the operating system behind nearly every CTF target. File permissions, search/pattern commands, redirection and piping are the daily toolkit.

### Questions

**Q4** (1 mark)
Which year and lab is credited with the original development of Unix?
- A) 1969, Bell Labs
- B) 1991, University of Helsinki
- C) 1998, MIT
- D) 1977, Xerox PARC

**Q5** (1 mark)
File permission `0600` on a Unix file means:
- A) Everyone can read and write it
- B) Only the owner has read + write access; no one else has any access
- C) Only the owner can execute it
- D) The file is world-readable but not writable

**Q6** (1 mark)
Which command searches for files or directories by name (or other criteria)?
- A) grep
- B) find
- C) cat
- D) touch

**Q7** (1 mark)
Which command searches for a text pattern _within_ file contents?
- A) find
- B) grep
- C) mkdir
- D) mv

**Q8** (1 mark)
In `ifconfig >> output.txt`, what does the `>>` operator do?
- A) Pipes output into another command
- B) Appends the command's output to a file
- C) Searches a file for a pattern
- D) Compares two files

**Q9** (1 mark)
The `|` symbol in a Unix command connects:
- A) The stdout of one command to the stdin of another
- B) Two files for comparison
- C) A file to a printer
- D) Two different users

**Q10** (1 mark)
Which command lets you securely remote-login to a CTF challenge server over the network?
- A) ftp
- B) ssh
- C) ping
- D) telnet

**Q11** (1 mark)
Which package manager is associated with Debian-based Linux distributions?
- A) YUM
- B) APT
- C) Homebrew
- D) dpkg alone

**Q12** (1 mark)
"On a UNIX system, everything is a file; if something is not a file, it is a ____."
- A) Folder
- B) Process
- C) Socket
- D) Kernel

**Q13** (1 mark)
Which command shows currently running processes, useful for CTF process monitoring?
- A) ps aux
- B) cd
- C) touch
- D) rm

---

## Section C: Programming for CTF

**Key ideas:** C and Python show up constantly in CTF challenges — C because reverse-engineering/binary-exploitation targets are usually written in it, Python because it's fast to prototype scripts and crackers in.

### Questions

**Q14** (1 mark)
Why does the lecture say C is important for red teaming/CTF, even though it is an old language?
- A) It is the only language that runs on Unix
- B) Most reverse-engineering and binary-exploitation CTF challenges are written in C
- C) It has built-in encryption functions
- D) It requires no compiler

**Q15** (1 mark)
C is a(n) ______ language, while Python is a(n) ______ language.
- A) interpreted; compiled
- B) compiled; interpreted
- C) both compiled
- D) both interpreted

**Q16** (1 mark)
The classical cipher used in the "shift cipher" CTF programming example (implemented in both C and Python) is the:
- A) AES cipher
- B) Caesar cipher
- C) RSA cipher
- D) Vigenère cipher

---

## Section D: Red-Teaming & CTF Tools

**Key ideas:** A handful of purpose-built tools cover common CTF categories: cracking password-protected archives, scanning web servers, and more.

### Questions

**Q17** (1 mark)
Which tool is described as "a fast password cracker… able to crack password protected zip files with brute force or dictionary-based attacks"?
- A) Nikto
- B) fcrackzip
- C) Nmap
- D) Wireshark

**Q18** (1 mark)
In the fcrackzip example, what does the `-u` flag do?
- A) Sets the username
- B) Unzips the file to verify a guessed password is actually correct
- C) Enables Unicode passwords
- D) Uploads the cracked result

**Q19** (1 mark)
Which tool is described as "a very light web penetration test tool… a pluggable web server and CGI scanner written in Perl"?
- A) fcrackzip
- B) Nikto
- C) SSH
- D) grep

**Q20** (1 mark)
To install software from source code on Unix, the typical three-step sequence is:
- A) apt, yum, brew
- B) ./configure, make, make install
- C) git clone, git pull, git push
- D) ssh, scp, sftp

---

## Answer Space

Leave space below each question for your working and final answer.

---

*Source: interactive version at `s3-red-teaming/session3-red-teaming.html`*
