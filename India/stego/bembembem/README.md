# [stego] bembembem

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

कठिनाई: hard
यहाँ निश्चित रूप से फ़्लैग है, लेकिन मुरिनो, मोलोचनोए से गुज़रना होगा और शायद कोटोस्ट से भी मिलना होगा

## चरण 0 — रिकॉनसेंस

file bembembem.mp4
ffprobe -v error -show_format -show_streams bembembem.mp4
exiftool bembembem.mp4
strings bembembem.mp4 | grep -iE 'BEM|b3m|flag'
exiftool/ffprobe में तुरंत संदिग्ध TikTok टैग नज़र आते हैं: aigc_info, comment=vid:..., vid_md5=6899efc8f52bffb08c5ac45deee24f64। अभी के लिए नोट कर लिया।

## चरण 1 — कस्टम uuid box ढूंढना

मानक MP4 में ftyp, moov, mdat आदि होते हैं। कोई भी अतिरिक्त uuid-ऐटम — लाल झंडा। top-level boxes पार्स करते हैं:
# mp4_walk.py
import struct, sys

![image.png](./images/img_1.png)

def walk(path: str) -> None:
    with open(path, "rb") as f:
        data = f.read()
    total = len(data)
    print(f"file size: {total}")
    print(f"{'offset':>12} {'size':>12}  type")

    pos = 0
    while pos < total:
        if total - pos < 8:
            print(f"  !! trailing {total - pos} bytes at {pos}")
            break
        size  = struct.unpack(">I", data[pos:pos + 4])[0]
        btype = data[pos + 4:pos + 8].decode("ascii", errors="replace")
        if size == 1:
            size = struct.unpack(">Q", data[pos + 8:pos + 16])[0]
        elif size == 0:
            size = total - pos
        print(f"{pos:>12} {size:>12}  {btype}")

        if size <= 0 or pos + size > total:
            print(f"  !! invalid box at {pos}, stopping walk")
            break
        pos += size

![image.png](./images/img_2.png)

if __name__ == "__main__":
    walk(sys.argv[1] if len(sys.argv) > 1 else "bembembem.mp4")

परिणाम:
0          32           b'ftyp'
32         3884477      b'moov'
3884509    8            b'free'
3884517    264587170    b'mdat'
268471687  970          b'uuid'      ← यही है
268472657  ...          कचरा (box नहीं)
uuid-बॉक्स की सामग्री पढ़ते हैं: 16 बाइट UUID + payload। UUID पहचानने योग्य: b3eb3eb3eb3eb3eb3eb3eb3eb3eb3eb3 (लेखक की सिग्नेचर)।
Payload BEM/v1\n# decode: base64 -> zlib inflate -> utf-8\n से शुरू होता है — प्रारूप पहली पंक्ति में ही दस्तावेज़ित है।
import base64, zlib
payload = data[268471687 + 8 + 16 : 268471687 + 970]
lines = payload.strip().split(b"\n")
b64 = b"".join(l for l in lines[1:] if not l.startswith(b"#"))
riddle = zlib.decompress(base64.b64decode(b64)).decode("utf-8")
print(riddle)
रूसी में तीन पद्यों वाला नोट मिलता है:
I. कानों से नहीं सुनना — ध्वनि के रंगों से देखना (नॉर्मलदाकी)।
   बयालीसवाँ मिनट, दस हज़ार से ऊपर (ओमायगाडनोस्ट)।
   जो स्पेक्ट्रम में फ़ुसफ़ुसाहट चित्रित करती है — वही कोडवर्ड।
   (केस महत्वपूर्ण, ठीक 8 कैरेक्टर।)
II. इस MP4 की लंबी पूँछ है। पूँछ पर मुहर लगी है —
   अंतिम ऐटम के बाद बोझ पड़ा है, दोहराती कुंजी से XOR।
   कुंजी पहले से मेटाडेटा में है, जानवर इसे माथे पर
   पहनता है: hex में vid_md5 (32 ASCII-कैरेक्टर)।
III. मुहर के नीचे — PK प्रारूप का पुराना संदूक।
    वह खोलो जो स्पेक्ट्रम ने फ़ुसफ़ुसाया।
    अंदर: अंगूर, बेर, हरे पर सेब, केले

## चरण 2 — 42वें मिनट पर स्पेक्ट्रोग्राम

ffmpeg -ss 2520 -i bembembem.mp4 -t 4 -vn -ac 1 probe.wav
sox probe.wav -n spectrogram -o spec.png -x 1400 -y 500
spec.png खोलते हैं — ~10.5–14.5 kHz रेंज में K0t05t पढ़ा जाता है (Sonic Visualiser / Audacity में भी दिखता है)।
पासवर्ड मिला: K0t05t।

## चरण 3 — मेटाडेटा से XOR-कुंजी

ffprobe -v error -show_entries format_tags=vid_md5 \
  -of default=nk=1:nw=1 bembembem.mp4
# 6899efc8f52bffb08c5ac45deee24f64
मान ठीक ASCII-स्ट्रिंग (32 कैरेक्टर) के रूप में — XOR की कुंजी।

## चरण 4 — पूँछ निकालना और डिक्रिप्ट करना

फ़ाइल की पूँछ uuid-बॉक्स के ठीक बाद, offset 268472657 से शुरू होती है:
KEY = b"6899efc8f52bffb08c5ac45deee24f64"
tail = data[268472657:]
plain = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(tail))
open("recovered.zip","wb").write(plain)
जाँच: plain[:4] == b'PK\\x03\\x04' — यह ZIP-मैजिक है। बढ़िया।
सटीक ऑफ़सेट जाने बिना वैकल्पिक तरीका: कुंजी के साथ XOR स्लाइडिंग-विंडो + डीकोडेड बफ़र में PK\\x03\\x04 सिग्नेचर खोजना। बिना डिक्रिप्शन के binwalk ZIP नहीं ढूंढेगा, क्योंकि XOR मैजिक तोड़ देता है — यही लेयर 3 छोड़ने की सज़ा है।

## चरण 5 — आर्काइव खोलना

unzip -P K0t05t recovered.zip
cat flag.txt
# KubSTU{3nj0y_1h_0f_M3ll57r0y_m3m3s}

## 🚩 फ़्लैग

```
KubSTU{3nj0y_1h_0f_M3ll57r0y_m3m3s}
```
