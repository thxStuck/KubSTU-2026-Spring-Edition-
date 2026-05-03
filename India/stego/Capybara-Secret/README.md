# [stego] Capybara Secret

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

## कार्य की जानकारी

- **श्रेणी:** स्टेगनोग्राफी
- **कठिनाई:** Medium
- **फ़्लैग:** `KubSTU{W0W_1ncred1ble_capyba6a}`

---

## चरण 1: छवि का विश्लेषण

`challenge.jpg` फ़ाइल प्राप्त करने पर, सबसे पहले इसमें छिपी जानकारी की जाँच करते हैं। स्टेगनोग्राफी में कई लोकप्रिय विधियाँ हैं:

- LSB (Least Significant Bit) — पिक्सेल के कम महत्वपूर्ण बिट्स में डेटा छिपाना
- मेटाडेटा (EXIF) — फ़ाइल की सेवा जानकारी में छिपाना
- फ़ाइल संयोजन — फ़ाइल के अंत में डेटा जोड़ना
- और अन्य...

सरल से शुरू करते हैं — मेटाडेटा की जाँच करें।

## चरण 2: EXIF-मेटाडेटा निकालना

### तरीका 1: ExifTool (अनुशंसित)

```bash
exiftool challenge.jpg
```

आउटपुट में कई फ़ील्ड दिखेंगे। **XP Comment** फ़ील्ड पर ध्यान दें:

```
XP Comment                      : XhoFGH{J0J_1aperq1oyr_pnclon6n}
```

### तरीका 2: Python + Pillow

```python
from PIL import Image
from PIL.ExifTags import TAGS

img = Image.open('challenge.jpg')
exif_data = img._getexif()

for tag_id, value in exif_data.items():
    tag = TAGS.get(tag_id, tag_id)
    print(f"{tag}: {value}")
```

### तरीका 3: ऑनलाइन सेवाएँ

ऑनलाइन EXIF viewer का उपयोग किया जा सकता है:

- <https://exifinfo.org/>
- <https://www.metadata2go.com/>

## चरण 3: पाई गई स्ट्रिंग का विश्लेषण

पाई गई स्ट्रिंग: `XhoFGH{J0J_1aperq1oyr_pnclon6n}`

यह स्ट्रिंग:

- फ़्लैग के प्रारूप जैसी दिखती है (संरचना `XXXXX{...}`)
- अपठनीय टेक्स्ट है
- संभवतः सरल सिफ़र से एन्क्रिप्टेड है

फ़्लैग का प्रारूप `KubSTU{...}` है, और हमें `XhoFGH{...}` दिखता है।

ROT13 सिफ़र की परिकल्पना जाँचते हैं:

- K → X (13 का शिफ्ट)
- u → h (13 का शिफ्ट)
- b → o (13 का शिफ्ट)
- ...

पैटर्न मिलता है — यह ROT13 है!

## चरण 4: ROT13 डिक्रिप्शन

### तरीका 1: ऑनलाइन डिकोडर

किसी भी ROT13 डिकोडर का उपयोग करें: <https://rot13.com/>

### तरीका 2: Python

```python
import codecs

encrypted = "XhoFGH{J0J_1aperq1oyr_pnclon6n}"
decrypted = codecs.decode(encrypted, 'rot_13')
print(decrypted)
```

### तरीका 3: Linux/Bash

```bash
echo "XhoFGH{J0J_1aperq1oyr_pnclon6n}" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

### तरीका 4: CyberChef

CyberChef में "ROT13" रेसिपी का उपयोग करें: <https://gchq.github.io/CyberChef/#recipe=ROT13(true,true,false,13)>

## समाधान

ROT13 लागू करने के बाद फ़्लैग प्राप्त होता है:

```
KubSTU{W0W_1ncred1ble_capyba6a}
```

---

## समाधान के लिए आवश्यक ज्ञान

1. **EXIF मेटाडेटा** — JPEG छवियों में मेटाडेटा होता है, जिसमें XPComment, XPKeywords जैसे गैर-मानक फ़ील्ड शामिल हैं (Windows-विशिष्ट)
2. **EXIF के साथ काम करने के उपकरण** — exiftool, Python लाइब्रेरी, ऑनलाइन सेवाएँ
3. **ROT13 सिफ़र** — एक सरल प्रतिस्थापन सिफ़र, जहाँ प्रत्येक अक्षर को वर्णमाला में 13 स्थान आगे के अक्षर से बदला जाता है। ROT13 स्वयं का उलटा है (दो बार लागू करने पर मूल टेक्स्ट वापस मिलता है)
4. **सावधानी** — जो कचरा जैसा दिखता है, वह हमेशा कचरा नहीं होता। एन्क्रिप्टेड डेटा अपठनीय दिख सकता है, लेकिन एक निश्चित संरचना रखता है

---

## वैकल्पिक स्वचालित सॉल्वर

```python
import struct
import codecs

def extract_xp_comment(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    pos = 2
    while pos < len(data) - 1:
        if data[pos] != 0xff:
            pos += 1
            continue
        marker = data[pos + 1]
        if marker == 0xe1:
            length = struct.unpack('>H', data[pos+2:pos+4])[0]
            segment = data[pos+4:pos+2+length]
            if segment[:6] == b'Exif\x00\x00':
                tiff = segment[6:]
                endian = '<' if tiff[:2] == b'II' else '>'
                ifd_off = struct.unpack(endian + 'I', tiff[4:8])[0]
                n = struct.unpack(endian + 'H', tiff[ifd_off:ifd_off+2])[0]
                for i in range(n):
                    e = ifd_off + 2 + i * 12
                    tag = struct.unpack(endian + 'H', tiff[e:e+2])[0]
                    if tag == 0x9C9C:
                        cnt = struct.unpack(endian + 'I', tiff[e+4:e+8])[0]
                        off = struct.unpack(endian + 'I', tiff[e+8:e+12])[0]
                        return tiff[off:off+cnt].decode('utf-16le').rstrip('\x00')
            pos += 2 + length
        elif 0xe0 <= marker <= 0xef or marker == 0xfe:
            pos += 2 + struct.unpack('>H', data[pos+2:pos+4])[0]
        else:
            break
    return None

encrypted = extract_xp_comment('challenge.jpg')
print(f"Encrypted: {encrypted}")
print(f"Flag: {codecs.decode(encrypted, 'rot_13')}")
```

---

## फ़्लैग

```
KubSTU{W0W_1ncred1ble_capyba6a}
```
