# [forensics] WirePass

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

Arctic intelligence detected anomalous activity in the secret network of the Penguin Command. According to intelligence sources, two field infrastructure nodes were transferring operational documents related to a military operation against Capybarovsk.

Our analysts managed to intercept a network dump, but it turned out the operatives weren't so simple: data was transmitted over an encrypted channel using a custom protocol.


[challenge.pcap](./files/challenge.pcap)

---

## Overview

We have a pcap file with network traffic between two nodes (172.20.0.2 and 172.20.0.3). Among a large amount of noise traffic (HTTP, DNS, FTP, ICMP, SYN scanning, TLS handshakes, random TCP/UDP), two key streams are hidden:

1. **Port 9999** — password transmitted in plaintext
2. **Port 31337** — encrypted ZIP archive transmitted via a custom binary protocol

---

## Step 1: Traffic Reconnaissance

We open `challenge.pcap` in Wireshark. We see ~1500 packets of various protocols.

We start by analyzing TCP streams. In Wireshark menu: **Statistics → Conversations → TCP**.

Among numerous connections, we find two interesting ones on non-standard ports:

- Connection on **port 9999** (small data volume)
- Connection on **port 31337** (noticeable volume of binary data)

### Filtering

```
tcp.port == 9999
```

---

## Step 2: Extracting the Password

We apply the filter `tcp.port == 9999` and open the TCP stream (**Follow → TCP Stream**).

We see:

```
PASS:IcyFl1pp3r$2026
ACK:OK
```

**Password:** `IcyFl1pp3r$2026`

> **Note:** The traffic contains FTP sessions with other passwords (`p@ssw0rd123`, `f1sh_l0ver`, etc.) — these are red herrings. The real password is transmitted on port 9999.

---

## Step 3: Binary Protocol Analysis

We filter traffic on port 31337:

```
tcp.port == 31337
```

We open the TCP stream (**Follow → TCP Stream**, display as **Raw/Hex**).

We see the data structure:

| Offset | Size | Field | Value |
|----|----|----|----|
| 0 | 4 | Magic | `58 46 45 52` ("XFER") |
| 4 | 16 | XOR key | `4a 7f 2b 91 de 33 a8 5c e1 6d f0 19 87 c4 55 3e` |
| 20 | 4 | Data length (BE) | Size of encrypted data |
| 24 | N | Data | XOR-encrypted ZIP archive |

---

## Step 4: Extraction and Decryption

### Option A: Manual (Python)

```python
import io
import struct
import pyzipper
from scapy.all import rdpcap, TCP, Raw

packets = rdpcap("challenge.pcap")

# Assemble TCP stream on port 31337 (data from client)
segments = []
for pkt in packets:
    if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt[TCP].dport == 31337:
        segments.append((pkt[TCP].seq, bytes(pkt[Raw].load)))

segments.sort(key=lambda x: x[0])
seen = set()
stream = b""
for seq, data in segments:
    if seq not in seen:
        seen.add(seq)
        stream += data

# Parse header
magic = stream[:4]        # b"XFER"
xor_key = stream[4:20]    # 16-byte XOR key
data_len = struct.unpack(">I", stream[20:24])[0]
encrypted = stream[24:24 + data_len]

# XOR decryption
decrypted = bytes([b ^ xor_key[i % 16] for i, b in enumerate(encrypted)])

# Extract from ZIP
buf = io.BytesIO(decrypted)
with pyzipper.AESZipFile(buf, 'r') as zf:
    zf.setpassword(b"IcyFl1pp3r$2026")
    for name in zf.namelist():
        print(f"--- {name} ---")
        print(zf.read(name).decode("utf-8"))
```

### Option B: Wireshark + CyberChef

1. In Wireshark: **Follow TCP Stream** (port 31337), format **Raw**, save as file `raw_stream.bin`
2. Cut off the first 4 bytes (magic "XFER")
3. Take bytes 4–19 — this is the XOR key
4. Take bytes 20–23 — length (big-endian)
5. Take data from byte 24 — encrypted archive
6. In CyberChef: **XOR** with the key → download result as `.zip`
7. Unzip with password `IcyFl1pp3r$2026`

---

## Step 5: Getting the Flag

The archive contains a file `mission_report.txt` — a report from the Penguin Command about the capture of Capybarovsk. At the end of the document:

```
SECRET OPERATION CODE: KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}
```

---

## Flag

```
KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}
```


