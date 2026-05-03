# [forensics] WirePass

> **श्रेणी:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

आर्कटिक खुफ़िया ने पेंगुइन कमांड के गुप्त नेटवर्क में असामान्य गतिविधि का पता लगाया। एजेंट डेटा के अनुसार, फ़ील्ड इंफ्रास्ट्रक्चर के दो नोड्स के बीच कैपीबारोव्स्क के विरुद्ध सैन्य अभियान से संबंधित ऑपरेशनल दस्तावेज़ों का हस्तांतरण हो रहा था।

हमारे विश्लेषकों ने नेटवर्क डंप इंटरसेप्ट करने में सफलता पाई, लेकिन पता चला कि ऑपरेटिव इतने सरल नहीं हैं: डेटा अपने स्वयं के प्रोटोकॉल का उपयोग करके एन्क्रिप्टेड चैनल से भेजा जा रहा था।


[challenge.pcap](./files/challenge.pcap)

---

## अवलोकन

एक pcap-फ़ाइल दी गई है जिसमें दो नोड्स (172.20.0.2 और 172.20.0.3) के बीच नेटवर्क ट्रैफ़िक है। बड़ी मात्रा में शोर ट्रैफ़िक (HTTP, DNS, FTP, ICMP, SYN-स्कैनिंग, TLS-हैंडशेक, रैंडम TCP/UDP) के बीच दो मुख्य स्ट्रीम छिपी हैं:

1. **पोर्ट 9999** — खुले रूप में पासवर्ड का हस्तांतरण
2. **पोर्ट 31337** — अपने बाइनरी प्रोटोकॉल द्वारा एन्क्रिप्टेड ZIP-आर्काइव का हस्तांतरण

---

## चरण 1: ट्रैफ़िक की रिकॉनेसेंस

`challenge.pcap` को Wireshark में खोलते हैं। विभिन्न प्रोटोकॉल के \~1500 पैकेट दिखते हैं।

TCP-स्ट्रीम के विश्लेषण से शुरू करते हैं। Wireshark मेनू में: **Statistics → Conversations → TCP**.

कई कनेक्शनों में से अमानक पोर्ट पर दो रोचक कनेक्शन मिलते हैं:

- **पोर्ट 9999** पर कनेक्शन (कम डेटा वॉल्यूम)
- **पोर्ट 31337** पर कनेक्शन (उल्लेखनीय बाइनरी डेटा वॉल्यूम)

### फ़िल्ट्रेशन

```
tcp.port == 9999
```

---

## चरण 2: पासवर्ड निकालना

फ़िल्टर `tcp.port == 9999` लगाते हैं और TCP-स्ट्रीम खोलते हैं (**Follow → TCP Stream**)।

दिखता है:

```
PASS:IcyFl1pp3r$2026
ACK:OK
```

**पासवर्ड:** `IcyFl1pp3r$2026`

> **नोट:** ट्रैफ़िक में अन्य पासवर्ड (`p@ssw0rd123`, `f1sh_l0ver` आदि) वाली FTP-सेशन हैं — ये गलत संकेत हैं। असली पासवर्ड पोर्ट 9999 पर भेजा जाता है।

---

## चरण 3: बाइनरी प्रोटोकॉल का विश्लेषण

पोर्ट 31337 पर ट्रैफ़िक फ़िल्टर करते हैं:

```
tcp.port == 31337
```

TCP-स्ट्रीम खोलते हैं (**Follow → TCP Stream**, **Raw/Hex** के रूप में दिखाएँ)।

डेटा की संरचना दिखती है:

| ऑफ़सेट | आकार | फ़ील्ड | मान |
|----|----|----|----|
| 0 | 4 | मैजिक | `58 46 45 52` ("XFER") |
| 4 | 16 | XOR-कुंजी | `4a 7f 2b 91 de 33 a8 5c e1 6d f0 19 87 c4 55 3e` |
| 20 | 4 | डेटा लंबाई (BE) | एन्क्रिप्टेड डेटा का आकार |
| 24 | N | डेटा | XOR-एन्क्रिप्टेड ZIP-आर्काइव |

---

## चरण 4: निष्कर्षण और डिक्रिप्शन

### विकल्प A: मैन्युअल (Python)

```python
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

# हेडर पार्स करना
magic = stream[:4]        # b"XFER"
xor_key = stream[4:20]    # 16-बाइट XOR-कुंजी
data_len = struct.unpack(">I", stream[20:24])[0]
encrypted = stream[24:24 + data_len]

# XOR-डिक्रिप्शन
decrypted = bytes([b ^ xor_key[i % 16] for i, b in enumerate(encrypted)])

# ZIP से निष्कर्षण
buf = io.BytesIO(decrypted)
with pyzipper.AESZipFile(buf, 'r') as zf:
    zf.setpassword(b"IcyFl1pp3r$2026")
    for name in zf.namelist():
        print(f"--- {name} ---")
        print(zf.read(name).decode("utf-8"))
```

### विकल्प B: Wireshark + CyberChef

1. Wireshark में: **Follow TCP Stream** (पोर्ट 31337), प्रारूप **Raw**, फ़ाइल `raw_stream.bin` के रूप में सहेजें
2. पहले 4 बाइट काटें (मैजिक "XFER")
3. बाइट 4–19 लें — यह XOR-कुंजी है
4. बाइट 20–23 लें — लंबाई (big-endian)
5. बाइट 24 से डेटा लें — एन्क्रिप्टेड आर्काइव
6. CyberChef में: कुंजी के साथ **XOR** → परिणाम `.zip` के रूप में डाउनलोड करें
7. पासवर्ड `IcyFl1pp3r$2026` से अनपैक करें

---

## चरण 5: फ़्लैग प्राप्त करना

आर्काइव में `mission_report.txt` फ़ाइल है — कैपीबारोव्स्क पर कब्ज़े के बारे में पेंगुइन कमांड की रिपोर्ट। दस्तावेज़ के अंत में:

```
СЕКРЕТНЫЙ КОД ОПЕРАЦИИ: KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}
```

---

## फ़्लैग

```
KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}
```


