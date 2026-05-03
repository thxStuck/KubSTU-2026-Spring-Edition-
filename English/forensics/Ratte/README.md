# [forensics] Ratte

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [Ratte.pcap](./files/img_1.pcap) | `pcap` |
| [rat.py](./files/img_2.py) | `py` |
| [rat.py](./files/img_3.py) | `py` |

</details>

---

You are an incident response specialist. Your company received a network traffic dump (pcap file) captured from one of the corporate network segments during suspicious activity. Analyze what's wrong here.

And once again we have suspicious traffic on the network. Everything seems standard but there's something that doesn't fit.

We open the file in Wireshark. We see tons of packets: HTTP requests to Google, DNS queries, some SSH, and a bunch of TCP packets. Over 1200 packets total. Going through them manually is a dead end — we need to look for anomalies.

## Structure

We open the file in Wireshark. We see tons of packets: HTTP requests to Google, DNS queries, some SSH, and a bunch of TCP packets. Over 1200 packets total. Going through them manually is a dead end — we need to look for anomalies.

Solution:
Statistics -> Conversations -> TCP. We see suspicious activity:

Port 1337 — not only does it stand out among the other ports, it has a fairly large volume. We apply the filter: tcp.port == 1337

We examine the first data packet from the client (10.0.0.5) to the server (10.0.0.15). The payload in HEX: de ad be ef 42. DEADBEEF is a classic "magic" session start marker. And what's the 42 at the end? Possibly some ID or an XOR key. Let's remember it: 0x42.

We look at the following packets in the same stream. They all start with byte 0xcc. Example of one packet: cc 1a 02 09 37. Breaking it down by bytes:
1. cc — looks like a frame start marker (Magic Byte).
2. 1a — some random byte (could be a packet ID or junk).
3. 02 — this looks like a data length. After it there are exactly 2 bytes: 09 37.

Let's try applying our key 0x42 to these bytes:
- 0x09 ^ 0x42 = 0x4b ('K')
- 0x37 ^ 0x42 = 0x75 ('u')

We got "Ku" — the beginning of the flag KubSTU. So the theory is correct: the flag is split into 2-character chunks, XOR-encrypted with key 0x42, and hidden in packets starting with 0xcc.

We create a script to extract and decode everything.

## 🚩 Flag

```
KubSTU{n0_m0r3_gr3pp1ng_1n_th3_d4rk_v2}
```
