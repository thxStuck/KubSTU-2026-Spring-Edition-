# [stego] bembembem

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

कठिनाई: hard

यहाँ निश्चित रूप से एक फ़्लैग है, लेकिन आपको मुरिनो, मोलोचनोए से गुज़रना होगा और संभवतः कोतोस्त से मुलाकात होगी


---

### चरण 0 — टोही

```bash
file bembembem.mp4
ffprobe -v error -show_format -show_streams bembembem.mp4
exiftool bembembem.mp4
strings bembembem.mp4 | grep -iE 'BEM|b3m|flag'
```

`exiftool`/`ffprobe` में तुरंत संदिग्ध TikTok टैग दिखाई देते हैं: `aigc_info`, `comment=vid:...`, `vid_md5=6899efc8f52bffb08c5ac45deee24f64`। फ़िलहाल नोट कर लिया।

### चरण 1 — कस्टम `uuid` box खोजना

मानक MP4 में `ftyp`, `moov`, `mdat` आदि होते हैं। कोई भी अतिरिक्त `uuid`-atom — एक लाल झंडा है। top-level boxes को पार्स करते हैं:

```python
# mp4_walk.py
import struct, sys


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


if __name__ == "__main__":
    walk(sys.argv[1] if len(sys.argv) > 1 else "bembembem.mp4")
    
```

परिणाम:

```
0          32           b'ftyp'
32         3884477      b'moov'
3884509    8            b'free'
3884517    264587170    b'mdat'
268471687  970          b'uuid'      ← यह रहा
268472657  ...          мусор (не box)
```

uuid-बॉक्स की सामग्री पढ़ते हैं: 16 बाइट UUID + payload। UUID पहचानने योग्य है: `b3eb3eb3eb3eb3eb3eb3eb3eb3eb3eb3` (लेखक का हस्ताक्षर)।

Payload `BEM/v1\n# decode: base64 -> zlib inflate -> utf-8\n` से शुरू होता है — प्रारूप स्वयं पहली पंक्ति में प्रलेखित है।

```python
import base64, zlib
payload = data[268471687 + 8 + 16 : 268471687 + 970]
lines = payload.strip().split(b"\n")
b64 = b"".join(l for l in lines[1:] if not l.startswith(b"#"))
riddle = zlib.decompress(base64.b64decode(b64)).decode("utf-8")
print(riddle)
```

तीन छंदों में रूसी भाषा में एक नोट प्राप्त होता है:

> I. कानों से नहीं सुनना — ध्वनि के रंगों से देखना (नॉर्मलडाकी)।
>
>    बयालीसवाँ मिनट, दस हज़ार से ऊपर (ओमायगाडनोस्त)।
>
>    स्पेक्ट्रम में फुसफुसाहट क्या चित्रित करती है — वही कोड शब्द है।
>
>    (रजिस्टर महत्वपूर्ण है, ठीक 8 अक्षर।)
>
> II. इस MP4 की लंबी पूँछ है। पूँछ सील की हुई है —
>
>    अंतिम atom के बाद एक भार है, जो दोहराई जाने वाली
>
>    कुंजी से XOR किया हुआ है। कुंजी पहले से ही फ़ाइल के
>
>    मेटाडेटा में है, जानवर इसे अपने माथे पर रखता है: hex में vid_md5
>
>    (32 ASCII-अक्षर)।
>
> III. सील के नीचे — PK प्रारूप का एक पुराना संदूक है।
>
>     स्पेक्ट्रम ने जो फुसफुसाया, उससे खोलो।
>
>     अंदर: अंगूर, बेर, हरे रंग पर सेब, केले

### चरण 2 — 42वें मिनट में स्पेक्ट्रोग्राम

```bash
ffmpeg -ss 2520 -i bembembem.mp4 -t 4 -vn -ac 1 probe.wav
sox probe.wav -n spectrogram -o spec.png -x 1400 -y 500
```

`spec.png` खोलते हैं — \~10.5–14.5 kHz रेंज में `K0t05t` पढ़ा जा सकता है (यह Sonic Visualiser / Audacity में भी दिखता है)।

पासवर्ड मिला: `K0t05t`।

### चरण 3 — मेटाडेटा से XOR-कुंजी

```bash
ffprobe -v error -show_entries format_tags=vid_md5 \
  -of default=nk=1:nw=1 bembembem.mp4
# 6899efc8f52bffb08c5ac45deee24f64
```

मान ठीक ASCII-स्ट्रिंग (32 अक्षर) के रूप में है — XOR के लिए कुंजी।

### चरण 4 — पूँछ निकालना और डिक्रिप्ट करना

फ़ाइल की पूँछ uuid-बॉक्स के ठीक बाद शुरू होती है, offset `268472657` पर:

```python
KEY = b"6899efc8f52bffb08c5ac45deee24f64"
tail = data[268472657:]
plain = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(tail))
open("recovered.zip","wb").write(plain)
```

जाँच: `plain[:4] == b'PK\x03\x04'` — यह ZIP-मैजिक है। बहुत अच्छा।

> *सटीक ऑफ़सेट जाने बिना वैकल्पिक तरीका:* कुंजी के साथ स्लाइडिंग-विंडो XOR + डिकोड किए गए बफ़र में `PK\x03\x04` सिग्नेचर की खोज। डिक्रिप्शन के बिना `binwalk` ZIP नहीं ढूँढ पाएगा, क्योंकि XOR मैजिक को तोड़ देता है — यही लेयर 3 छोड़ने का जुर्माना है।

### चरण 5 — आर्काइव खोलना

```bash
unzip -P K0t05t recovered.zip
cat flag.txt
# KubSTU{3nj0y_1h_0f_M3ll57r0y_m3m3s}
```

---

फ़्लैग - `KubSTU{3nj0y_1h_0f_M3ll57r0y_m3m3s}`
