# Session 1 · Cryptography

**Personal Study Notes · Printable Worksheet**
**21 questions · 24 marks**

This document contains all questions from the interactive sheet in a printable format. Write your answers directly in your notebook, then self-check afterwards using the interactive `.html` version.

---

## Section A: Core Concepts

**Key ideas:** Cryptology splits into **cryptography** (defending information) and **cryptanalysis** (attacking it). Modern schemes are designed under **Kerckhoffs's principle**: assume attackers know every algorithm involved — only the short secret key stays hidden.

### Questions

**Q1** (1 mark)
"Cryptology" is made up of two branches: cryptography (which defends) and ______ (which attacks).
- A) Cryptanalysis
- B) Steganography
- C) Digital forensics
- D) Obfuscation

**Q2** (1 mark)
In the classic Alice / Bob / Eve / Mallory terminology, who represents an attacker who can only _eavesdrop_, not modify data?
- A) Alice
- B) Bob
- C) Eve
- D) Mallory

**Q3** (1 mark)
Kerckhoffs's principle assumes attackers already know everything about a cryptosystem _except_:
- A) The ciphertext
- B) The algorithm used
- C) The secret key
- D) The plaintext length

**Q4** (1 mark)
A classical substitution cipher maps 27 symbols (26 letters + a space character) to 27 symbols, giving 27! possible keys. Roughly how many _bits_ are needed to represent one key (log₂(27!))?
- A) About 27 bits
- B) About 94 bits
- C) About 128 bits
- D) About 256 bits

**Q5** (1 mark)
Why is exhaustive (brute-force) search infeasible against a 27!-key substitution cipher, per the lecture's back-of-envelope estimate?
- A) Computers cannot perform XOR operations
- B) It would take roughly as long as the solar system has left to exist
- C) The algorithm itself is a state secret
- D) No computer can generate random numbers

---

## Section B: Classical Ciphers & Attacks

**Key ideas:** Substitution ciphers aren't secure against a determined attacker: a known plaintext reveals the key directly, and even a ciphertext-only attacker can exploit the fact that English letters (and letter pairs) occur with predictable frequency.

### Questions

**Q6** (1 mark)
Classical substitution ciphers can be broken with only a ciphertext (no known plaintext) using:
- A) Quantum computing
- B) Frequency analysis of letters/letter-pairs
- C) SQL injection
- D) The birthday paradox

**Q7** (1 mark)
According to the lecture, roughly how much ciphertext is "sufficiently long" for frequency analysis to reliably break a substitution cipher in English?
- A) 5 characters
- B) 50 characters
- C) 500 characters
- D) 5000 characters

**Q8** (1 mark)
Given a known plaintext/ciphertext pair for a substitution cipher, an attacker can recover the key by:
- A) Running the AES key schedule backwards
- B) Matching up corresponding plaintext and ciphertext letters directly
- C) Guessing randomly until the checksum matches
- D) Waiting for the algorithm to be leaked online

---

## Section C: Modern Ciphers & Modes

**Key ideas:** AES is the workhorse modern block cipher — but a block cipher only encrypts one fixed-size block. Extending that to real (large) messages needs a **mode of operation**, and the choice of mode matters enormously for security.

### Questions

**Q9** (2 marks)
Select all TRUE statements about AES (select all that apply): *(select ALL that apply)*
- A) Block length is 128 bits
- B) Key length can be 128, 192, or 256 bits
- C) Proposed to NIST in 2000 through an open, worldwide selection process
- D) Designed by Ron Rivest in 1987

**Q10** (1 mark)
Which block-cipher mode of operation is known for leaking plaintext patterns — e.g. an encrypted image's flat background stays visible — because identical plaintext blocks always produce identical ciphertext blocks?
- A) CTR
- B) GCM
- C) ECB
- D) CBC

**Q11** (1 mark)
Among the AES modes mentioned in the lecture, which is described as the most secure, able to withstand attackers who can probe a "decryption oracle"?
- A) ECB
- B) CTR
- C) CBC
- D) GCM

**Q12** (2 marks)
In CTR mode, what happens if the same key _and_ the same IV (nonce) are mistakenly reused to encrypt two different messages, X and Y?
- A) The ciphertext becomes shorter
- B) XOR-ing the two ciphertexts cancels the shared keystream, leaking X⊕Y
- C) The AES algorithm simply refuses to run
- D) Nothing — CTR mode is immune to IV reuse

---

## Section D: Pitfalls & Side Channels

**Key ideas:** Modern ciphers like AES are believed mathematically secure — but real systems are broken through _implementation_ mistakes, not by breaking the maths.

### Questions

**Q13** (1 mark)
A key derived from an 8-character password (e.g. via SHA3), even when it feeds 128-bit AES, is realistically only as strong as:
- A) The full 2¹²⁸ AES keyspace
- B) The much smaller password-guessing space
- C) The SHA3 output size (256+ bits)
- D) It cannot be attacked at all

**Q14** (1 mark)
"Security through obscurity" failed for RC4 and MIFARE Classic because:
- A) Both were open-source from day one
- B) Their secret algorithms were eventually leaked or reverse-engineered, exposing real weaknesses
- C) Both used quantum-resistant algorithms
- D) Neither was ever deployed in production

**Q15** (1 mark)
A side-channel attack is best defined as one that:
- A) Exploits a mathematical weakness in the cipher's core algorithm
- B) Uses information (often physical — power, timing, sound) outside the cipher's abstract security model
- C) Only works against quantum computers
- D) Requires directly breaking AES

**Q16** (2 marks)
Which of these are side-channel attack techniques mentioned in the lecture? (select all) *(select ALL that apply)*
- A) Power analysis on a smartcard
- B) Acoustic cryptanalysis (keystroke / 3D-printer sound)
- C) SQL injection
- D) Electromagnetic emissions from an LCD panel
- E) Cache/page-fault timing on trusted hardware like Intel SGX

**Q17** (1 mark)
Which real CVE example from the lecture illustrates a "predictable key generation" pitfall?
- A) CVE-2020-7010: a Kubernetes cloud app generating passwords from deployment time
- B) Heartbleed leaking OpenSSL memory
- C) The BEAST attack on TLS 1.0
- D) ZeroLogon's static AES-CFB8 IV

---

## Section E: History & Real-World Failures

**Key ideas:** Cryptography has a long track record of ciphers that looked strong when introduced, then fell to advances in cryptanalysis or plain hardware progress.

### Questions

**Q18** (1 mark)
DES, standardized in 1977 with a 56-bit key, was practically broken in 1998 by:
- A) Quantum computers
- B) A dedicated brute-force machine cracking a key in about 56 hours
- C) A side-channel power-analysis attack
- D) Reverse-engineering the algorithm

**Q19** (1 mark)
RC4 became insecure in real deployments primarily because:
- A) It was mathematically broken from the very first day
- B) WEP's use of RC4 with weak/reused IVs was exploited, and the industry moved to WPA2/AES
- C) It required specialised hardware nobody owned
- D) It was never actually implemented anywhere

**Q20** (1 mark)
During WWII, the Enigma machine's secret key was set physically using its:
- A) Keyboard layout alone
- B) Rotors and plugboard settings
- C) Lampboard bulbs
- D) Power cable

**Q21** (1 mark)
Triple DES is still in limited use today with an effective key strength of about:
- A) 56 bits
- B) 112 bits
- C) 168 bits
- D) 256 bits

---

## Answer Space

Leave space below each question for your working and final answer.

---

*Source: interactive version at `s1-cryptography/session1-cryptography.html`*
