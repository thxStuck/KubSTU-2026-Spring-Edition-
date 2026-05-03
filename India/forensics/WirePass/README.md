# [forensics] WirePass

> **श्रेणी:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [challenge.pcap](./files/img_1.pcap) | `pcap` |

</details>

---

आर्कटिक खुफ़िया ने पेंगुइन कमांड के गुप्त नेटवर्क में असामान्य गतिविधि दर्ज की। एजेंट जानकारी के अनुसार, फ़ील्ड इन्फ्रास्ट्रक्चर के दो नोड्स के बीच कैपीबारोव्स्क के खिलाफ़ सैन्य ऑपरेशन से संबंधित ऑपरेशनल दस्तावेज़ों का हस्तांतरण हो रहा था।
हमारे विश्लेषक नेटवर्क डंप इंटरसेप्ट करने में सफल रहे, लेकिन पता चला कि ऑपरेटिव इतने सरल नहीं हैं: अपने प्रोटोकॉल का उपयोग करके एन्क्रिप्टेड चैनल से डेटा भेजा गया था।

अवलोकन
दो नोड्स (172.20.0.2 और 172.20.0.3) के बीच नेटवर्क ट्रैफ़िक वाली pcap-फ़ाइल दी गई है। बड़ी मात्रा में शोर ट्रैफ़िक (HTTP, DNS, FTP, ICMP, SYN-स्कैनिंग, TLS-हैंडशेक, रैंडम TCP/UDP) के बीच दो मुख्य स्ट्रीम छिपी हैं:
पोर्ट 9999 — पासवर्ड का ओपन टेक्स्ट में ट्रांसमिशन
पोर्ट 31337 — कस्टम बाइनरी प्रोटोकॉल से एन्क्रिप्टेड ZIP-आर्काइव का ट्रांसमिशन

## चरण 1: ट्रैफ़िक रिकॉनसेंस

challenge.pcap को Wireshark में खोलते हैं। विभिन्न प्रोटोकॉल के ~1500 पैकेट दिखते हैं।
TCP-स्ट्रीम के विश्लेषण से शुरू करते हैं। Wireshark मेनू में: Statistics → Conversations → TCP।
अनेक कनेक्शनों में दो रोचक नॉन-स्टैंडर्ड पोर्ट पर मिलते हैं:
पोर्ट 9999 पर कनेक्शन (कम डेटा वॉल्यूम)
पोर्ट 31337 पर कनेक्शन (बाइनरी डेटा का बड़ा वॉल्यूम)
फ़िल्टरिंग
tcp.port == 9999

## चरण 2: पासवर्ड निकालना

tcp.port == 9999 फ़िल्टर लगाते हैं और TCP-स्ट्रीम खोलते हैं (Follow → TCP Stream)।
दिखता है:
PASS:IcyFl1pp3r$2026
ACK:OK
पासवर्ड: IcyFl1pp3r$2026
नोट: ट्रैफ़िक में अन्य पासवर्ड वाले FTP-सेशन हैं (p@ssw0rd123, f1sh_l0ver आदि) — ये भ्रामक संकेत हैं। असली पासवर्ड पोर्ट 9999 पर भेजा जाता है।

## चरण 3: बाइनरी प्रोटोकॉल का विश्लेषण

पोर्ट 31337 का ट्रैफ़िक फ़िल्टर करते हैं:
tcp.port == 31337
TCP-स्ट्रीम खोलते हैं (Follow → TCP Stream, Raw/Hex के रूप में दिखाएं)।
डेटा संरचना दिखती है:
ऑफ़सेट
आकार
फ़ील्ड
मान
0
4
मैजिक
58 46 45 52 ("XFER")
4
16
XOR-कुंजी
4a 7f 2b 91 de 33 a8 5c e1 6d f0 19 87 c4 55 3e
20
4
डेटा लंबाई (BE)
एन्क्रिप्टेड डेटा का आकार
24
N
डेटा
XOR-एन्क्रिप्टेड ZIP-आर्काइव

## चरण 4: निकालना और डिक्रिप्शन

विकल्प A: मैन्युअल (Python)
import io
import struct
import pyzipper
from scapy.all import rdpcap, TCP, Raw

packets = rdpcap("challenge.pcap")

# पोर्ट 31337 पर TCP-स्ट्रीम एकत्र करना (क्लाइंट से डेटा)
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

# हेडर पार्सिंग
magic = stream[:4]        # b"XFER"
xor_key = stream[4:20]    # 16-बाइट XOR-कुंजी
data_len = struct.unpack(">I", stream[20:24])[0]
encrypted = stream[24:24 + data_len]

# XOR-डिक्रिप्शन
decrypted = bytes([b ^ xor_key[i % 16] for i, b in enumerate(encrypted)])

# ZIP से निकालना
buf = io.BytesIO(decrypted)
with pyzipper.AESZipFile(buf, 'r') as zf:
    zf.setpassword(b"IcyFl1pp3r$2026")
    for name in zf.namelist():
        print(f"--- {name} ---")
        print(zf.read(name).decode("utf-8"))
विकल्प B: Wireshark + CyberChef
Wireshark में: Follow TCP Stream (पोर्ट 31337), Raw प्रारूप, raw_stream.bin के रूप में सेव करें
पहले 4 बाइट काटें (मैजिक "XFER")
बाइट 4–19 लें — यह XOR-कुंजी है
बाइट 20–23 लें — लंबाई (big-endian)
बाइट 24 से डेटा लें — एन्क्रिप्टेड आर्काइव
CyberChef में: कुंजी से XOR → परिणाम .zip के रूप में डाउनलोड करें
पासवर्ड IcyFl1pp3r$2026 से अनपैक करें

## चरण 5: फ़्लैग प्राप्त करना

आर्काइव में mission_report.txt फ़ाइल है — कैपीबारोव्स्क पर कब्ज़े के बारे में पेंगुइन कमांड की रिपोर्ट। दस्तावेज़ के अंत में:
गुप्त ऑपरेशन कोड: KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}

## 🚩 फ़्लैग

```
KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}
```
