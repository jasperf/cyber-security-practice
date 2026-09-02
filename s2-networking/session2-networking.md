# Session 2 · Networking Fundamentals

**IJCO/SIMCC Cyber Security · Printable Worksheet**
**21 questions · 22 marks**

This document contains all questions from the interactive sheet in a printable format. Write your answers directly in your notebook, then self-check afterwards using the interactive `.html` version.

---

## Section A: Communication & the OSI Model

**Key ideas:** The **OSI model** (ISO 7498, 1984) splits network communication into 7 layers, from the physical wire up to the application a user sees. Real-world TCP/IP collapses several of these together, but the concepts still map across.

### Questions

**Q1** (1 mark)
The OSI (Open System Interconnect) model has how many layers?
- A) 4
- B) 5
- C) 7
- D) 8

**Q2** (1 mark)
Which OSI layer ensures data is in a usable format and is where encryption occurs?
- A) Application
- B) Presentation
- C) Session
- D) Transport

**Q3** (1 mark)
In the simplified TCP/IP layer model used in the lecture, which layer "decides the path of the data"?
- A) Transport
- B) Network
- C) Datalink
- D) Physical

**Q4** (1 mark)
Which protocol operates at the Application layer, used for resolving network names?
- A) TCP
- B) ARP
- C) DNS
- D) Ethernet

---

## Section B: IP Addressing

**Key ideas:** An IPv4 address splits into a **network identifier** and a **host identifier** using the subnet mask: `IP AND subnet mask = network identifier`. **CIDR** notation (e.g. `/20`) generalises this to any bit-length split.

### Questions

**Q5** (1 mark)
IPv4 addresses are 32 bits, giving 2³² unique addresses. Roughly how many billion is that? (nearest whole number)
_(numeric answer)_

**Q6** (1 mark)
Given IP address `172.16.254.1` and subnet mask `255.255.0.0`, what is the network identifier?
- A) 172.16.0.0
- B) 172.0.0.0
- C) 172.16.254.0
- D) 0.0.254.1

**Q7** (2 marks)
Which of these are reserved **private** IPv4 ranges? (select all) *(select ALL that apply)*
- A) 10.x.x.x
- B) 172.16.x.x – 172.31.x.x
- C) 192.168.x.x
- D) 8.8.8.x

**Q8** (1 mark)
In CIDR notation, an address written as `192.4.16/20` means:
- A) The address has 20 host bits
- B) The leading 20 bits are the shared network number
- C) It is an IPv6 address
- D) The subnet mask is 255.255.255.0

**Q9** (1 mark)
NAT (Network Address Translation) works by:
- A) Encrypting packets end-to-end
- B) Rewriting IP address information in packet headers as they cross a routing device
- C) Resolving domain names to IP addresses
- D) Splitting large packets into fragments

**Q10** (1 mark)
IPv6 uses how many bits per address, compared with IPv4's 32?
- A) 64
- B) 96
- C) 128
- D) 256

---

## Section C: TCP, UDP & the Handshake

**Key ideas:** TCP is **reliable, ordered, and connection-oriented** (3-way handshake, sequence numbers, ACKs). UDP is **lightweight and connectionless** — no delivery guarantees, no setup overhead.

### Questions

**Q11** (1 mark)
Which transport-layer protocol offers a reliable, in-order, connection-oriented "stream of bytes" using a 3-way handshake?
- A) UDP
- B) IP
- C) TCP
- D) ARP

**Q12** (1 mark)
In the TCP 3-way handshake, what is the correct order of flags exchanged between Host A (initiator) and Host B?
- A) ACK, SYN, SYN-ACK
- B) SYN, SYN-ACK, ACK
- C) SYN-ACK, SYN, ACK
- D) SYN, ACK, SYN-ACK

**Q13** (1 mark)
UDP is best described as:
- A) Reliable, ordered, connection-oriented
- B) Simple, lightweight, "unreliable" message delivery with no handshake
- C) Used exclusively for HTTP traffic
- D) A routing protocol

---

## Section D: Ports & Scanning

**Key ideas:** Port numbers split into three ranges by convention, and scanning them can reveal what services a host is running — useful for defenders and attackers alike. **Scanning without permission is illegal.**

### Questions

**Q14** (1 mark)
Which port range is reserved as "Well Known Ports" for standard services like HTTP and SMTP?
- A) 0–1023
- B) 1024–49151
- C) 49152–65535
- D) 1–65535

**Q15** (1 mark)
Ports 49152–65535 are known as:
- A) Well Known Ports
- B) Registered Ports
- C) Dynamic / Private (Ephemeral) Ports
- D) Reserved Ports

**Q16** (1 mark)
A "SYN scan" (half-open / stealth scan) differs from a full TCP Connect scan because:
- A) It never sends any packets at all
- B) After receiving SYN-ACK, it sends a RESET instead of completing the handshake
- C) It only works over UDP
- D) It encrypts all scan traffic

**Q17** (1 mark)
Why are UDP port scans described as slower and less reliable than TCP scans?
- A) UDP packets are physically larger
- B) There is no acknowledgment confirming a packet was received (UDP is "stateless")
- C) UDP is always blocked by every firewall
- D) UDP requires its own 3-way handshake

---

## Section E: Hands-On Networking Tools

**Key ideas:** A handful of command-line tools cover most day-to-day network diagnosis and reconnaissance.

### Questions

**Q18** (1 mark)
Which command-line tool tests whether a host is reachable across an IP network and reports the reply time?
- A) netstat
- B) ping
- C) ifconfig
- D) hostname

**Q19** (1 mark)
Which tool reports each router "hop" and the elapsed time along the path to a destination?
- A) traceroute
- B) netstat
- C) grep
- D) nmap

**Q20** (1 mark)
Which tool shows a host's current routing-table entries, active connections, and listening ports?
- A) ping
- B) netstat
- C) traceroute
- D) hostname

**Q21** (1 mark)
Which of these is a _network scanning_ tool for discovering live hosts, open ports, and running services — not a packet sniffer?
- A) Wireshark
- B) Ettercap
- C) Nmap
- D) tcpdump

---

## Answer Space

Leave space below each question for your working and final answer.

---

*Source: interactive version at `s2-networking/session2-networking.html`*
