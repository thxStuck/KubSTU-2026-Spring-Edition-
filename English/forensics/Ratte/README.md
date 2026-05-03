# [forensics] Ratte

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

## You are an incident response specialist. Your company received a network traffic dump (pcap file) captured from one of the corporate network segments during suspicious activity. Analyze what went wrong here.

You are an incident response specialist. Your company received a network traffic dump (pcap file) captured from one of the corporate network segments during suspicious activity.  

You are an incident response specialist. Your company received a network traffic dump (pcap file) captured from one of the corporate network segments during suspicious activity.  

Once again we have suspicious traffic on the network. Everything seems standard, but there's something that doesn't fit.

[Ratte.pcap](./files/Ratte.pcap)

hmmm

We open the file in Wireshark. We see a bunch of packets: HTTP requests to Google, DNS queries, some SSH, and lots of TCP packets. Over 1200 packets total. Going through them manually is a dead end — we need to look for anomalies.  

### We open the file in Wireshark. We see a bunch of packets: HTTP requests to Google, DNS queries, some SSH, and lots of TCP packets. Over 1200 packets total. Going through them manually is a dead end — we need to look for anomalies.  

## Structure

We open the file in Wireshark. We see a bunch of packets: HTTP requests to Google, DNS queries, some SSH, and lots of TCP packets. Over 1200 packets total. Going through them manually is a dead end — we need to look for anomalies.  

##  Solution 

Statistics -> Conversations -> TCP. We see strange activity:

 

 ![img_1.png](./images/img_1.png)

Port 1337 — not only does it stand out among the other ports, it also has a fairly large volume. We apply the filter: tcp.port == 1337  


 ![img_2.png](./images/img_2.png)

  We look at the first data packet from the client (10.0.0.5) to the server (10.0.0.15). The payload in HEX: de ad be ef 42. DEADBEEF — a classic "magic" session start marker. And what's that 42 at the end? It could be some kind of ID or an XOR key. Let's remember it: 0x42 

We look at the next packets in the same stream. They all start with byte 0xcc. Example of one packet: cc 1a 02 09 37. Breaking it down byte by byte:

1.cc — looks like a frame start marker (Magic Byte).

2.1a — some random byte (could be a packet ID or junk).

3.02 — this looks like the data length. After it there are exactly 2 bytes: 09 37.

Let's try applying our key 0x42 to these bytes:

•0x09 ^ 0x42 = 0x4b ('K')

•0x37 ^ 0x42 = 0x75 ('u')

We got "Ku" — the beginning of the flag KubSTU. So the theory is correct: the flag is split into 2-character chunks, XOR-encrypted with key 0x42, and hidden in packets starting with 0xcc.

 Let's create a script that extracts and decodes everything.


[rat.py](./files/rat.py)

Flag: KubSTU{n0_m0r3_gr3pp1ng_1n_th3_d4rk_v2}  