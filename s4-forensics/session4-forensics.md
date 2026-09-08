# Session 4 · Digital Forensics

**Personal Study Notes · Printable Worksheet**
**19 questions · 21 marks**

This document contains all questions from the interactive sheet in a printable format. Write your answers directly in your notebook, then self-check afterwards using the interactive `.html` version.

---

## Section A: Fundamentals & Process

**Key ideas:** Digital forensics uncovers evidence from electronic devices — recovering deleted files, examining traffic logs, analysing memory — and follows a defined 6-stage process to keep that evidence admissible.

### Questions

**Q1** (1 mark)
Digital forensics is best defined as:
- A) Writing secure application code
- B) The field of investigation and analysis focused on uncovering digital evidence from electronic devices and systems
- C) Penetration testing a live network
- D) Designing firewalls

**Q2** (2 marks)
What are the six stages of the digital forensics process, in order?
- A) Collection &rarr; Analysis &rarr; Identification &rarr; Presentation &rarr; Examination &rarr; Preservation
- B) Identification &rarr; Preservation &rarr; Collection &rarr; Examination &rarr; Analysis &rarr; Presentation
- C) Preservation &rarr; Identification &rarr; Analysis &rarr; Collection &rarr; Examination &rarr; Presentation
- D) Analysis &rarr; Presentation &rarr; Identification &rarr; Collection &rarr; Preservation &rarr; Examination

**Q3** (1 mark)
"Preservation" in the forensics process is primarily about:
- A) Securing and protecting evidence so it stays unaltered and remains admissible
- B) Presenting findings to a jury
- C) Recovering deleted files
- D) Installing forensic software

**Q4** (2 marks)
Which of these are listed as the four types of digital evidence in the lecture? (select all) *(select ALL that apply)*
- A) File system artifacts
- B) Network traffic logs
- C) Social media follower counts
- D) Memory dumps
- E) Mobile device data

**Q5** (1 mark)
A memory dump (RAM capture) is especially valuable in forensics because it can reveal:
- A) Only deleted files from years ago
- B) Running processes, open files, network connections, and encryption keys live at capture time
- C) Only the file system's folder structure
- D) Nothing useful &mdash; it is just noise

**Q6** (1 mark)
Which tool is specifically named for memory analysis in the forensic tools list?
- A) EnCase
- B) Volatility
- C) Autopsy
- D) Wireshark

**Q7** (1 mark)
Which tool is specifically named for network traffic analysis?
- A) FTK
- B) EnCase
- C) Wireshark
- D) Autopsy

**Q8** (1 mark)
File metadata such as timestamps, permissions, and deletion/recovery records fall under which evidence category?
- A) Network traffic logs
- B) Mobile device data
- C) Memory dumps
- D) File system artifacts

**Q9** (1 mark)
Base64 encoding represents binary data using how many characters from the ASCII set?
- A) 2
- B) 16
- C) 64
- D) 256

**Q10** (1 mark)
Hexadecimal ("hex") encoding is a base-____ number system.
- A) 2
- B) 8
- C) 16
- D) 64

**Q11** (1 mark)
Which encoding scheme is named alongside Base64 and URL encoding as commonly appearing in CTF flag-decoding challenges?
- A) ROT13
- B) bcrypt
- C) SHA-256
- D) RSA-2048

**Q12** (1 mark)
Which Linux command lists hidden files (those starting with a dot) in a directory?
- A) ls -a
- B) find /etc
- C) cat -h
- D) grep -r

**Q13** (1 mark)
On Windows, which command-line option reveals hidden files in a directory listing?
- A) dir /ah
- B) dir /s
- C) dir /w
- D) dir /p

**Q14** (1 mark)
Which forensic technique involves hiding data inside an image, audio, or other file so it is not visible without special tools?
- A) Steganography
- B) Encoding
- C) Hashing
- D) Tokenization

**Q15** (1 mark)
In the scenario about a suspect's encrypted smartphone, what is the core challenge posed by strong encryption?
- A) It makes the phone slower
- B) It is illegal for law enforcement to attempt decryption
- C) It corrupts file timestamps
- D) Without the decryption key, forensic analysts cannot access the data at all

**Q16** (1 mark)
"Anti-forensic techniques" (file wiping, data overwriting, etc.) are used by perpetrators to:
- A) Speed up file transfers
- B) Encrypt communications for privacy compliance
- C) Erase or obfuscate digital evidence and cover their tracks
- D) Improve system performance

**Q17** (1 mark)
Which regulations are named as introducing challenges around data access/privacy during forensic investigations?
- A) HIPAA and SOX
- B) GDPR and CCPA
- C) PCI-DSS and ISO 27001
- D) FISMA and NIST 800-53

**Q18** (1 mark)
"Cloud forensics" is concerned with:
- A) Forensics performed only on weather-prediction systems
- B) Recovering paper documents
- C) Analysing IoT device firmware
- D) Collecting, preserving, and analysing evidence stored on remote cloud platforms

**Q19** (1 mark)
What real-world example does the lecture give for the relevance of "IoT forensics"?
- A) Analysing a firewall's logs
- B) Analysing a corporate laptop's hard drive
- C) Recovering deleted emails from a mail server
- D) A voice-activated smart home assistant possibly recording audio evidence relevant to a crime
